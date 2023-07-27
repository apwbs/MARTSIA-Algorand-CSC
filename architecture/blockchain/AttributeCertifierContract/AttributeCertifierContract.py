from algosdk.atomic_transaction_composer import *
from pyteal import *


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
            opt_in=OnCompleteAction(action=Approve(), call_config=CallConfig.CALL),
        ),
    )

    @router.method(no_op=CallConfig.CALL)
    def on_save(process_id: abi.String, ipfs_link: abi.String) -> Expr:
        return Seq(
            App.globalPut(processID, process_id.get()),
            App.globalPut(IPFSLink, ipfs_link.get()),
        )

    return router
