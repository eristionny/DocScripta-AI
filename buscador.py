import urllib.request
import urllib.parse
import json
import xml.etree.ElementTree as ET

def buscar_pubmed(termo, max_resultados=2):
    try:
        termo_codificado = urllib.parse.quote(termo)
        url_busca = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term={termo_codificado}&retmax={max_resultados}&retmode=json"
        
        req = urllib.request.urlopen(url_busca)
        dados = req.read().decode('utf-8')
        
        ids = json.loads(dados)['esearchresult']['idlist']
        
        if not ids:
            return "Nenhum artigo encontrado."

        ids_str = ",".join(ids)
        url_detalhes = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id={ids_str}&retmode=xml"
        req_detalhes = urllib.request.urlopen(url_detalhes)
        xml_data = req_detalhes.read()

        root = ET.fromstring(xml_data)
        artigos = []

        for article in root.findall('.//PubmedArticle'):
            titulo_elem = article.find('.//ArticleTitle')
            titulo = titulo_elem.text if titulo_elem is not None else "Título não disponível"
            
            autor = article.find('.//Author/LastName')
            sobrenome = autor.text.upper() if autor is not None else "AUTOR"
            
            ano_elem = article.find('.//Journal/JournalIssue/PubDate/Year')
            ano = ano_elem.text if ano_elem is not None else "2026"

            pmid = article.find('.//MedlineCitation/PMID').text
            link = f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"

            artigos.append({
                "titulo": titulo,
                "citacao_abnt": f"({sobrenome} et al., {ano})",
                "link": link
            })

        return artigos
    except Exception as e:
        return f"Erro na busca: {str(e)}"