from pydantic import BaseModel, Field


class AnalyzeRequest(BaseModel):
    sequence: str = Field(min_length=1)
    strand_type: str | None = None


class CodonAminoRow(BaseModel):
    codon: str
    amino_acid_name: str
    three_letter: str
    one_letter: str


class AnalyzeResponse(BaseModel):
    sequence_type: str
    detection_explanation: str
    transcription_explanation: str
    translation_explanation: str
    amino_acid_explanation: str
    protein_explanation: str
    normalized_input: str
    strand_type: str | None
    mrna_sequence: str
    codon_rows: list[CodonAminoRow]
    polypeptide_chain: list[CodonAminoRow]
    protein_sequence: str
    protein_characterization: dict


class ProteinLookupResponse(BaseModel):
    source: str
    status: str
    message: str
    hits: list[dict]
