from collections import defaultdict
from datetime import UTC, datetime
from json import dump, load
from os import environ

from grpc import RpcError, insecure_channel

from .grpc.app.proxyman.command.command_pb2 import AddUserOperation
from .grpc.app.proxyman.command.command_pb2 import AlterInboundRequest
from .grpc.app.proxyman.command.command_pb2 import RemoveUserOperation
from .grpc.app.proxyman.command.command_pb2_grpc import HandlerServiceStub
from .grpc.app.stats.command.command_pb2 import GetAllOnlineUsersRequest
from .grpc.app.stats.command.command_pb2 import QueryStatsRequest
from .grpc.app.stats.command.command_pb2_grpc import StatsServiceStub
from .grpc.common.protocol.user_pb2 import User
from .grpc.common.serial.typed_message_pb2 import TypedMessage
from .grpc.proxy.vless.account_pb2 import Account as VLESSAccount
from .grpc.proxy.vmess.account_pb2 import Account as VMessAccount
from ui.settings import BASE_DIR

XRAY_API = f'xray:{environ["XRAY_API_PORT"]}'
XRAY_CONFIG = BASE_DIR / 'config.json'


class Xray:
    def __init__(self):
        with open(XRAY_CONFIG) as file:
            self._config = load(file)

    def _write(self):
        with open(XRAY_CONFIG, 'w') as file:
            dump(self._config, file, indent=4)

    def add_user(self, user):
        try:
            with insecure_channel(XRAY_API) as channel:
                stub = HandlerServiceStub(channel)
                account = VLESSAccount(flow=user['flow'], id=user['id'])
                operation = AddUserOperation(
                    user=User(
                        account=TypedMessage(
                            type=account.DESCRIPTOR.full_name,
                            value=account.SerializeToString(),
                        ),
                        email=user['email'],
                        level=user['level'],
                    )
                )
                stub.AlterInbound(
                    AlterInboundRequest(
                        operation=TypedMessage(
                            type=operation.DESCRIPTOR.full_name,
                            value=operation.SerializeToString(),
                        ),
                        tag='vless',
                    )
                )
                account = VMessAccount(id=user['id'])
                operation = AddUserOperation(
                    user=User(
                        account=TypedMessage(
                            type=account.DESCRIPTOR.full_name,
                            value=account.SerializeToString(),
                        ),
                        email=user['email'],
                        level=user['level'],
                    )
                )
                stub.AlterInbound(
                    AlterInboundRequest(
                        operation=TypedMessage(
                            type=operation.DESCRIPTOR.full_name,
                            value=operation.SerializeToString(),
                        ),
                        tag='vmess',
                    )
                )
        except RpcError:
            pass

        for inbound in self._config['inbounds']:
            if inbound['tag'] == 'vless':
                inbound['settings']['clients'].append(user)
            elif inbound['tag'] == 'vmess':
                inbound['settings']['clients'].append(
                    {key: user[key] for key in user if key != 'flow'}
                )

        self._write()

    def init(self):
        for inbound in self._config['inbounds']:
            if inbound['tag'] == 'vless':
                inbound['settings']['clients'] = []
                inbound['settings']['decryption'] = environ['XRAY_VLESS_DECRYPTION']
                inbound['streamSettings']['xhttpSettings']['path'] = environ[
                    'XRAY_VLESS_PATH'
                ]
            elif inbound['tag'] == 'vmess':
                inbound['settings']['clients'] = []
                inbound['streamSettings']['xhttpSettings']['path'] = environ[
                    'XRAY_VMESS_PATH'
                ]

        self._write()

    def online(self):
        emails = []

        try:
            with insecure_channel(XRAY_API) as channel:
                stub = StatsServiceStub(channel)
                response = stub.GetAllOnlineUsers(GetAllOnlineUsersRequest())

                for user in response.users:
                    _, email, _ = user.split('>>>')
                    emails.append(email)
        except RpcError:
            pass

        return emails

    def remove_user(self, email):
        try:
            with insecure_channel(XRAY_API) as channel:
                stub = HandlerServiceStub(channel)
                operation = RemoveUserOperation(email=email)
                stub.AlterInbound(
                    AlterInboundRequest(
                        operation=TypedMessage(
                            type=operation.DESCRIPTOR.full_name,
                            value=operation.SerializeToString(),
                        ),
                        tag='vless',
                    )
                )
                stub.AlterInbound(
                    AlterInboundRequest(
                        operation=TypedMessage(
                            type=operation.DESCRIPTOR.full_name,
                            value=operation.SerializeToString(),
                        ),
                        tag='vmess',
                    )
                )
        except RpcError:
            pass

        removed = False

        for inbound in self._config['inbounds']:
            if inbound['tag'] in ['vless', 'vmess']:
                i = -1

                for j, client in enumerate(inbound['settings']['clients']):
                    if client['email'] == email:
                        i = j
                        break

                if i >= 0:
                    del inbound['settings']['clients'][i]
                    removed = True

        if not removed:
            return

        self._write()

    def stats(self):
        stats = defaultdict(dict)

        try:
            with insecure_channel(XRAY_API) as channel:
                now = str(datetime.now(UTC))
                stub = StatsServiceStub(channel)
                response = stub.QueryStats(QueryStatsRequest(pattern='', reset=True))

                for stat in response.stat:
                    _, email, _, link = stat.name.split('>>>')
                    stats[email]['created_at'] = now
                    stats[email][link] = stat.value
        except RpcError:
            pass

        return stats
