from algosdk.atomic_transaction_composer import *
from pyteal import *

messageID = Bytes("msg_id")
IPFSLink = Bytes("ipfs_link")

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
      App.globalPut(messageID, Int(0)),
      App.globalPut(IPFSLink, Int(0)), 
      Approve(),
    )


def getRouter():
    router = Router(
        "StorageMessageContract",
        BareCallActions(
            no_op=OnCompleteAction.create_only(handle_creation),
            update_application=OnCompleteAction.always(Reject()),
            delete_application=OnCompleteAction.always(Reject()),
            close_out=OnCompleteAction.never(),
            opt_in=OnCompleteAction(action=Approve(), call_config=CallConfig.CALL),
        ),
    )

    @router.method(no_op=CallConfig.CALL)
    def approveDataOwner(account: abi.Account) -> Expr:
        return Seq(
            Assert(
                Txn.sender() == Global.creator_address(),
            ),
            App.localPut(account.address(), LocalState.approved_key, Int(2)),
            Approve()
        )
    

    @router.method(no_op=CallConfig.CALL)
    def revokeDataOwner(account: abi.Account) -> Expr:
        return Seq(
            Assert(
                Txn.sender() == Global.creator_address(),
                App.localGet(account.address(), LocalState.approved_key) == Int(2),
            ),
            App.localPut(account.address(), LocalState.approved_key, Int(0)),
            Approve()
        )


    @router.method(no_op=CallConfig.CALL)
    def on_save(message_id: abi.String, ipfs_link: abi.String) -> Expr:
        return Seq(
            Assert(
                App.localGet(Txn.sender(), LocalState.approved_key) == Int(2),
            ),
            App.globalPut(messageID, message_id.get()),
            App.globalPut(IPFSLink, ipfs_link.get()),
        )

    return router
