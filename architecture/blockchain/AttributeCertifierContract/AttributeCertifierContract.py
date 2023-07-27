from algosdk.atomic_transaction_composer import *
from pyteal import *


processID = Bytes("process_id")
IPFSLink = Bytes("ipfs_link")

handle_creation = Seq(
    App.globalPut(processID, Int(0)),
    App.globalPut(IPFSLink, Int(0)),
    Approve(),
)


def getRouter():
    router = Router(
        "StorageAttributesContract",
        BareCallActions(
            no_op=OnCompleteAction.create_only(handle_creation),
            update_application=OnCompleteAction.always(Reject()),
            delete_application=OnCompleteAction.always(Reject()),
            close_out=OnCompleteAction.never(),
        ),
    )

    @router.method(no_op=CallConfig.CALL)
    def on_save(process_id: abi.String, ipfs_link: abi.String) -> Expr:
        return Seq(
            Assert(
                Txn.sender() == Global.creator_address(),
            ),
            App.globalPut(processID, process_id.get()),
            App.globalPut(IPFSLink, ipfs_link.get()),
        )

    return router
