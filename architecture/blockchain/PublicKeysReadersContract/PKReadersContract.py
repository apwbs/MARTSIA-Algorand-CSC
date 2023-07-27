from algosdk.atomic_transaction_composer import *
from pyteal import *

reader_address = Bytes("readerAddress")
pk_reader_ipfs_link = Bytes("pk_ipfs_link")

class LocalInts:
    approved_key = Bytes("approved")

class LocalState(LocalInts):
    @staticmethod
    def num_uints():
        return len(static_attrs(LocalInts))

    @classmethod
    def schema(cls):
        return StateSchema(
            num_uints=cls.num_uints(),
        )
    
handle_creation = Seq(
      App.globalPut(reader_address, Global.zero_address()),
      App.globalPut(pk_reader_ipfs_link, Int(0)), 
      Approve(),
    )


def getRouter():
    router = Router(
        "StoreReaderPublicKeyContract",
        BareCallActions(
            no_op=OnCompleteAction.create_only(handle_creation),
            update_application=OnCompleteAction.always(Reject()),
            delete_application=OnCompleteAction.always(Reject()),
            close_out=OnCompleteAction.never(),
            opt_in=OnCompleteAction(action=Approve(), call_config=CallConfig.CALL),
        ),
    )

    @router.method(no_op=CallConfig.CALL)
    def approveReader(account: abi.Account) -> Expr:
        return Seq(
            Assert(
                Txn.sender() == Global.creator_address(),
            ),
            App.localPut(account.address(), LocalState.approved_key, Int(3)),
            Approve()
        )
    
    @router.method(no_op=CallConfig.CALL)
    def revokeReader(account: abi.Account) -> Expr:
        return Seq(
            Assert(
                Txn.sender() == Global.creator_address(),
                App.localGet(account.address(), LocalState.approved_key) == Int(3),
            ),
            App.localPut(account.address(), LocalState.approved_key, Int(0)),
            Approve()
        )

    @router.method(no_op=CallConfig.CALL)
    def on_save(ipfs_link: abi.String) -> Expr:
        return Seq(
            Assert(
                App.localGet(Txn.sender(), LocalState.approved_key) == Int(3),
            ),
            App.globalPut(reader_address, Txn.sender()),
            App.globalPut(pk_reader_ipfs_link, ipfs_link.get()),
        )

    return router
    