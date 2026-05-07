import httpx


async def lookup_uniprot(protein_sequence: str) -> dict:
    if not protein_sequence:
        return {
            "source": "UniProt",
            "status": "skipped",
            "message": "No protein sequence available for lookup.",
            "hits": [],
        }

    query = f"sequence:{protein_sequence}"
    url = "https://rest.uniprot.org/uniprotkb/search"
    params = {"query": query, "format": "json", "size": 3}

    async with httpx.AsyncClient(timeout=15.0) as client:
        try:
            response = await client.get(url, params=params)
            response.raise_for_status()
            payload = response.json()
        except Exception as exc:  # noqa: BLE001
            return {
                "source": "UniProt",
                "status": "error",
                "message": f"UniProt lookup failed: {exc}",
                "hits": [],
            }

    results = payload.get("results", [])
    hits = []
    for item in results:
        protein_desc = item.get("proteinDescription", {})
        rec_name = protein_desc.get("recommendedName", {})
        full_name = rec_name.get("fullName", {}).get("value", "Unknown protein")
        organism = item.get("organism", {}).get("scientificName", "Unknown organism")
        function_text = "Function not listed"
        comments = item.get("comments", [])
        for comment in comments:
            if comment.get("commentType") == "FUNCTION":
                texts = comment.get("texts", [])
                if texts:
                    function_text = texts[0].get("value", function_text)
                    break

        hits.append(
            {
                "accession": item.get("primaryAccession", "N/A"),
                "protein_name": full_name,
                "organism": organism,
                "function": function_text,
            }
        )

    status = "ok" if hits else "empty"
    message = (
        "UniProt returned potential matches for your protein sequence."
        if hits
        else "UniProt was queried, but no direct matches were returned for this sequence."
    )

    return {
        "source": "UniProt",
        "status": status,
        "message": message,
        "hits": hits,
    }


async def lookup_blast_placeholder(protein_sequence: str) -> dict:
    if not protein_sequence:
        return {
            "source": "BLAST",
            "status": "skipped",
            "message": "BLAST skipped because no protein sequence was produced.",
            "hits": [],
        }

    return {
        "source": "BLAST",
        "status": "pending",
        "message": "BLAST integration placeholder is active. UniProt results are shown now; BLAST polling can be added next.",
        "hits": [],
    }
