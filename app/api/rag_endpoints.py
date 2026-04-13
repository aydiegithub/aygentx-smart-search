from fastapi import APIRouter, Depends, Query, Response
from fastapi.responses import JSONResponse
from datetime import datetime
from app.api.dependencies import verify_api_key
from app.models.pydantic.schemas import (
    RagUpdateRequest,
    RagUpdateResponse,
    RagUpdateMetadata,
    RagIndicesResponse,
    RagDownloadResponse
)
from app.services.rag_service import RagService
from app.core.config import settings

router = APIRouter(prefix="/rag", tags=["RAG"])
rag_service = RagService()


@router.post("/update", response_model=RagUpdateResponse, dependencies=[Depends(verify_api_key)])
async def update_rag(request: RagUpdateRequest):
    try:
        metadata = await rag_service.process_update(
            content=request.content,
            update_mode=request.update_mode,
            model_name=request.model
        )

        msg_map = {
            "clear": "Knowledge base successfully cleared. All raw documents and tree nodes deleted.",
            "replace": "Knowledge base completely replaced.",
            "merge": "Successfully merged new content with existing knowledge base and regenerated the tree."
        }

        return RagUpdateResponse(
            status='success',
            message=msg_map.get(request.update_mode, "Update successful."),
            metadata=RagUpdateMetadata(**metadata)
        )

    except Exception as e:
        return JSONResponse(
            status_code=500, content={
                "status": "error",
                "message": str(e)
            }
        )


@router.get("/indices", response_model=RagIndicesResponse, dependencies=[Depends(verify_api_key)])
async def get_indices():
    try:
        data = rag_service.get_indices()
        return RagIndicesResponse(
            status="success",
            total_nodes=data["total_nodes"],
            tree=data["tree"]
        )

    except Exception as e:
        return JSONResponse(status_code=500,
                            content={
                                "status": "error",
                                "message": str(e)
                            })


@router.get("/download", response_class=Response, dependencies=[Depends(verify_api_key)])
async def download_backup(file: bool = Query(False, description="Set to true to download as a file")):
    try:
        raw_docs = rag_service.get_raw_documents()
        tree_data = rag_service.get_indices()["tree"]

        timestamp = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        file_timestamp = datetime.utcnow().strftime("%Y-%m-%d-%H-%M")

        response_data = RagDownloadResponse(
            status="success",
            backup_date=timestamp,
            raw_documents=raw_docs,
            knowledge_tree=tree_data
        )

        if file:
            filename = f"{file_timestamp}{settings.download_file_name}"
            return JSONResponse(
                content=response_data.model_dump(),
                headers={
                    "Content-Disposition": f'attachment; filename="{filename}"'}
            )

        return response_data
    except Exception as e:
        return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})
