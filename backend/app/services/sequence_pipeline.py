from collections import Counter

DNA_BASES = {"A", "C", "G", "T"}
RNA_BASES = {"A", "C", "G", "U"}

CODON_TABLE = {
    "UUU": ("Phenylalanine", "Phe", "F"),
    "UUC": ("Phenylalanine", "Phe", "F"),
    "UUA": ("Leucine", "Leu", "L"),
    "UUG": ("Leucine", "Leu", "L"),
    "CUU": ("Leucine", "Leu", "L"),
    "CUC": ("Leucine", "Leu", "L"),
    "CUA": ("Leucine", "Leu", "L"),
    "CUG": ("Leucine", "Leu", "L"),
    "AUU": ("Isoleucine", "Ile", "I"),
    "AUC": ("Isoleucine", "Ile", "I"),
    "AUA": ("Isoleucine", "Ile", "I"),
    "AUG": ("Methionine", "Met", "M"),
    "GUU": ("Valine", "Val", "V"),
    "GUC": ("Valine", "Val", "V"),
    "GUA": ("Valine", "Val", "V"),
    "GUG": ("Valine", "Val", "V"),
    "UCU": ("Serine", "Ser", "S"),
    "UCC": ("Serine", "Ser", "S"),
    "UCA": ("Serine", "Ser", "S"),
    "UCG": ("Serine", "Ser", "S"),
    "CCU": ("Proline", "Pro", "P"),
    "CCC": ("Proline", "Pro", "P"),
    "CCA": ("Proline", "Pro", "P"),
    "CCG": ("Proline", "Pro", "P"),
    "ACU": ("Threonine", "Thr", "T"),
    "ACC": ("Threonine", "Thr", "T"),
    "ACA": ("Threonine", "Thr", "T"),
    "ACG": ("Threonine", "Thr", "T"),
    "GCU": ("Alanine", "Ala", "A"),
    "GCC": ("Alanine", "Ala", "A"),
    "GCA": ("Alanine", "Ala", "A"),
    "GCG": ("Alanine", "Ala", "A"),
    "UAU": ("Tyrosine", "Tyr", "Y"),
    "UAC": ("Tyrosine", "Tyr", "Y"),
    "UAA": ("Stop", "Stop", "*"),
    "UAG": ("Stop", "Stop", "*"),
    "CAU": ("Histidine", "His", "H"),
    "CAC": ("Histidine", "His", "H"),
    "CAA": ("Glutamine", "Gln", "Q"),
    "CAG": ("Glutamine", "Gln", "Q"),
    "AAU": ("Asparagine", "Asn", "N"),
    "AAC": ("Asparagine", "Asn", "N"),
    "AAA": ("Lysine", "Lys", "K"),
    "AAG": ("Lysine", "Lys", "K"),
    "GAU": ("Aspartic acid", "Asp", "D"),
    "GAC": ("Aspartic acid", "Asp", "D"),
    "GAA": ("Glutamic acid", "Glu", "E"),
    "GAG": ("Glutamic acid", "Glu", "E"),
    "UGU": ("Cysteine", "Cys", "C"),
    "UGC": ("Cysteine", "Cys", "C"),
    "UGA": ("Stop", "Stop", "*"),
    "UGG": ("Tryptophan", "Trp", "W"),
    "CGU": ("Arginine", "Arg", "R"),
    "CGC": ("Arginine", "Arg", "R"),
    "CGA": ("Arginine", "Arg", "R"),
    "CGG": ("Arginine", "Arg", "R"),
    "AGU": ("Serine", "Ser", "S"),
    "AGC": ("Serine", "Ser", "S"),
    "AGA": ("Arginine", "Arg", "R"),
    "AGG": ("Arginine", "Arg", "R"),
    "GGU": ("Glycine", "Gly", "G"),
    "GGC": ("Glycine", "Gly", "G"),
    "GGA": ("Glycine", "Gly", "G"),
    "GGG": ("Glycine", "Gly", "G"),
}


def normalize_sequence(raw_sequence: str) -> str:
    lines = [line.strip() for line in raw_sequence.splitlines() if line.strip()]
    no_headers = [line for line in lines if not line.startswith(">")]
    return "".join(no_headers).replace(" ", "").upper()


def detect_sequence_type(sequence: str) -> tuple[str, str]:
    chars = set(sequence)

    if not sequence:
        return "invalid", "No sequence was found after cleaning the input."

    if "T" in chars and "U" in chars:
        return (
            "invalid",
            "The sequence includes both T and U. DNA uses T while RNA uses U, so mixing both means the input is not a valid single DNA or RNA sequence.",
        )

    if chars.issubset(DNA_BASES):
        return (
            "dna",
            f"All {len(sequence)} characters are from A, C, G, and T, so the input is DNA.",
        )

    if chars.issubset(RNA_BASES):
        return (
            "rna",
            f"All {len(sequence)} characters are from A, C, G, and U, so the input is RNA.",
        )

    invalid_chars = sorted(chars.difference(DNA_BASES.union(RNA_BASES)))
    return (
        "invalid",
        "The sequence has invalid characters: "
        + ", ".join(invalid_chars)
        + ". Valid DNA/RNA bases are A, C, G, T, and U.",
    )


def transcribe(sequence: str, sequence_type: str, strand_type: str | None) -> tuple[str, str, str | None]:
    if sequence_type == "rna":
        explanation = (
            "Transcription creates mRNA from DNA. Because your input is already RNA, the mRNA sequence is the same as your input."
        )
        return sequence, explanation, None

    if strand_type not in {"template", "non-template"}:
        raise ValueError("For DNA input, strand_type must be 'template' or 'non-template'.")

    if strand_type == "non-template":
        mrna = sequence.replace("T", "U")
        explanation = (
            "You selected non-template (coding) DNA. Coding DNA has the same message as mRNA except DNA uses T where RNA uses U, so each T was replaced by U."
        )
        return mrna, explanation, strand_type

    complement = {"A": "U", "T": "A", "C": "G", "G": "C"}
    mrna = "".join(complement[b] for b in sequence)
    explanation = (
        "You selected template DNA. mRNA is built as the complementary sequence: A->U, T->A, C->G, and G->C, giving the transcribed RNA shown."
    )
    return mrna, explanation, strand_type


def translate_mrna(mrna: str) -> tuple[list[dict], list[dict], str, str]:
    codon_rows: list[dict] = []
    chain: list[dict] = []
    protein_letters: list[str] = []

    for i in range(0, len(mrna) - 2, 3):
        codon = mrna[i : i + 3]
        amino_name, three_letter, one_letter = CODON_TABLE.get(codon, ("Unknown", "Unk", "?"))
        row = {
            "codon": codon,
            "amino_acid_name": amino_name,
            "three_letter": three_letter,
            "one_letter": one_letter,
        }
        codon_rows.append(row)

        if amino_name == "Stop":
            break

        if amino_name != "Unknown":
            chain.append(row)
            protein_letters.append(one_letter)

    explanation = (
        "Translation reads mRNA three bases at a time (codons). Each codon maps to one amino acid based on the genetic code. "
        "Reading stopped at the first stop codon, if present."
    )
    return codon_rows, chain, "".join(protein_letters), explanation


def characterize_protein(protein_sequence: str) -> dict:
    counts = Counter(protein_sequence)
    total = len(protein_sequence)
    composition = {
        aa: {"count": count, "percent": round((count / total) * 100, 2) if total else 0}
        for aa, count in sorted(counts.items())
    }
    return {
        "length": total,
        "composition": composition,
        "note": "This summary shows which amino acids appear most in your protein chain.",
    }


def explain_amino_acids() -> str:
    return (
        "Amino acids are the small building blocks of proteins. During translation, the ribosome links amino acids in order to form a polypeptide chain. "
        "That chain then folds to become a functional protein."
    )


def explain_protein() -> str:
    return (
        "A protein is a folded chain of amino acids. The order of amino acids determines the protein's structure and likely function. "
        "Database matches can suggest similar known proteins and their biological roles."
    )
