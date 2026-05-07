import json

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user
from app.models.analysis_run import AnalysisRun
from app.models.user import User
from app.schemas.analysis import AnalyzeRequest, AnalyzeResponse, ProteinLookupResponse
from app.services.protein_lookup import lookup_blast_placeholder, lookup_uniprot
from app.services.sequence_pipeline import (
    characterize_protein,
    detect_sequence_type,
    explain_amino_acids,
    explain_protein,
    normalize_sequence,
    transcribe,
    translate_mrna,
)

router = APIRouter(prefix="/analysis", tags=["analysis"])


async def build_analysis(sequence: str, strand_type: str | None) -> AnalyzeResponse:
    normalized = normalize_sequence(sequence)
    sequence_type, detection_explanation = detect_sequence_type(normalized)

    if sequence_type == "invalid":
        raise HTTPException(status_code=400, detail=detection_explanation)

    mrna, transcription_explanation, resolved_strand = transcribe(normalized, sequence_type, strand_type)
    codon_rows, chain, protein_sequence, translation_explanation = translate_mrna(mrna)
    protein_characterization = characterize_protein(protein_sequence)

    return AnalyzeResponse(
        sequence_type=sequence_type,
        detection_explanation=detection_explanation,
        transcription_explanation=transcription_explanation,
        translation_explanation=translation_explanation,
        amino_acid_explanation=explain_amino_acids(),
        protein_explanation=explain_protein(),
        normalized_input=normalized,
        strand_type=resolved_strand,
        mrna_sequence=mrna,
        codon_rows=codon_rows,
        polypeptide_chain=chain,
        protein_sequence=protein_sequence,
        protein_characterization=protein_characterization,
    )


@router.post("/run", response_model=AnalyzeResponse)
async def run_analysis(
    payload: AnalyzeRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    result = await build_analysis(payload.sequence, payload.strand_type)

    run = AnalysisRun(
        user_id=user.id,
        sequence_type=result.sequence_type,
        strand_type=result.strand_type,
        input_sequence=result.normalized_input,
        mrna_sequence=result.mrna_sequence,
        protein_sequence=result.protein_sequence,
        summary_json=result.model_dump_json(),
    )
    db.add(run)
    db.commit()

    return result


@router.post("/run-file", response_model=AnalyzeResponse)
async def run_analysis_from_file(
    file: UploadFile = File(...),
    strand_type: str | None = None,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    data = await file.read()
    text = data.decode("utf-8", errors="ignore")
    result = await build_analysis(text, strand_type)

    run = AnalysisRun(
        user_id=user.id,
        sequence_type=result.sequence_type,
        strand_type=result.strand_type,
        input_sequence=result.normalized_input,
        mrna_sequence=result.mrna_sequence,
        protein_sequence=result.protein_sequence,
        summary_json=result.model_dump_json(),
    )
    db.add(run)
    db.commit()

    return result


@router.get("/history")
def list_history(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    rows = (
        db.query(AnalysisRun)
        .filter(AnalysisRun.user_id == user.id)
        .order_by(AnalysisRun.created_at.desc())
        .limit(20)
        .all()
    )
    return [
        {
            "id": row.id,
            "sequence_type": row.sequence_type,
            "strand_type": row.strand_type,
            "protein_sequence": row.protein_sequence,
            "created_at": row.created_at,
        }
        for row in rows
    ]


@router.get("/history/{run_id}")
def get_history_run(
    run_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    row = db.query(AnalysisRun).filter(AnalysisRun.id == run_id, AnalysisRun.user_id == user.id).first()
    if not row:
        raise HTTPException(status_code=404, detail="History item not found")

    return json.loads(row.summary_json)


@router.post("/protein-lookup", response_model=list[ProteinLookupResponse])
async def protein_lookup(
    protein_sequence: str,
    _user: User = Depends(get_current_user),
):
    uniprot = await lookup_uniprot(protein_sequence)
    blast = await lookup_blast_placeholder(protein_sequence)
    return [uniprot, blast]
