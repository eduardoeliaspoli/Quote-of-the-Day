import requests
from bs4 import BeautifulSoup
import json
import os
import time

# --- CONFIGURAÇÃO ---

# 1. CONFIGURE AQUI OS SITES QUE VOCÊ QUER RASPAR
#    - tipo: 'blog' (raspa apenas a URL única)
#    - tipo: 'paginado' (raspa a 'url_base' + /1, /2, ... até 'paginas')
SITES_CONFIG = [
    
    # --- FOCO: Frases do Bem ---
    {
        "tipo": "paginado",
        "nome": "Frases do Bem (Motivação)",
        "url_base": "https://www.frasesdobem.com.br/frases-de-motivacao/",
        "paginas": 1, 
        "seletor_card": "div.card-body",
        "seletor_frase": "p[itemprop='text']",
        "seletor_autor": "div.autor"
    },
    {
        "tipo": "paginado",
        "nome": "Frases do Bem (Otimismo)",
        "url_base": "https://www.frasesdobem.com.br/frases-de-otimismo/", 
        "paginas": 10, 
        "seletor_card": "div.card-body",
        "seletor_frase": "p[itemprop='text']",
        "seletor_autor": "div.autor"
    },
    {
        "tipo": "paginado",
        "nome": "Frases do Bem (Confiança)",
        "url_base": "https://www.frasesdobem.com.br/frases-de-confianca/", 
        "paginas": 10, 
        "seletor_card": "div.card-body",
        "seletor_frase": "p[itemprop='text']",
        "seletor_autor": "div.autor"
    },
    {
        "tipo": "paginado",
        "nome": "Frases do Bem (Esperança)",
        "url_base": "https://www.frasesdobem.com.br/frases-de-esperanca/", 
        "paginas": 10, 
        "seletor_card": "div.card-body",
        "seletor_frase": "p[itemprop='text']",
        "seletor_autor": "div.autor"
    },
    
    # --- SITE ADICIONADO ANTERIORMENTE ---
    {
        "tipo": "paginado",
        "nome": "Belas Mensagens",
        "url_base": "https://www.belasmensagens.com.br/motivacao/", # Página 2 é /page/2
        "paginas": 9, 
        "seletor_card": "div.grid-item.card", 
        "seletor_frase": "div[itemprop='text'] p",
        "seletor_autor": "p.autor a" 
    },
    
    # --- NOVO SITE ADICIONADO AGORA ---
    {
        "tipo": "paginado",
        "nome": "Frases Top (Reflexão)",
        "url_base": "https://www.frasestop.com/frases-de-reflexao/", # Página 2 é /2/
        "paginas": 10, 
        "seletor_card": "div.card-phrase", 
        "seletor_frase": "span.phrase-title",
        "seletor_autor": "span.phrase-author span" 
    },

    # --- OUTROS SITES (Reativados) ---
    {
        "tipo": "paginado",
        "nome": "Mundo das Mensagens",
        "url_base": "https://www.mundodasmensagens.com/frases-motivacao/", # Página 2 é /2
        "paginas": 10,
        "seletor_card": "article.card-phrase", 
        "seletor_frase": "p.description",
        "seletor_autor": "span.author"
    },
    {
        "tipo": "paginado",
        "nome": "Frases de Motivação",
        "url_base": "https://www.frasesdemotivacao.com.br/", # Página 2 é /pagina/2/
        "paginas": 10,
        "seletor_card": "div.tMain",
        "seletor_frase": "p.tCont",
        "seletor_autor": "p.tAuto"
    },
    {
        "tipo": "paginado",
        "nome": "Frases de Inspiração",
        "url_base": "https://www.frasesdeinspiracao.com.br/", # Página 2 é /pagina/2
        "paginas": 10,
        "seletor_card": "article.phrase-card",
        "seletor_frase": "p.phrase",
        "seletor_autor": "span.author"
    },
]

# 2. NOME DO SEU ARQUIVO JSON
ARQUIVO_JSON = "frases.json"

# 3. CABEÇALHO PARA PARECER UM NAVEGADOR (EVITA BLOQUEIOS SIMPLES)
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

# 4. LISTA DE SITES CUJA PAGINAÇÃO NÃO TERMINA COM /
#    Ex: site.com/frases/2 (em vez de site.com/frases/2/)
SITES_PAGINACAO_SEM_BARRA = ["mundodasmensagens.com", "frasesdeinspiracao.com.br", "frasesdobem.com.br"] 

# --- FIM DA CONFIGURAÇÃO ---


def carregar_frases_existentes():
    """Carrega frases do JSON para evitar duplicatas."""
    if not os.path.exists(ARQUIVO_JSON):
        return [], set() 

    try:
        with open(ARQUIVO_JSON, "r", encoding="utf-8") as f:
            lista_de_frases = json.load(f)
        
        frases_existentes_set = set(item['frase'] for item in lista_de_frases if 'frase' in item)
        print(f"Carregadas {len(lista_de_frases)} frases existentes.")
        return lista_de_frases, frases_existentes_set

    except json.JSONDecodeError:
        print(f"Erro: O arquivo {ARQUIVO_JSON} está vazio ou mal formatado. Começando do zero.")
        return [], set()
    except Exception as e:
        print(f"Erro ao carregar {ARQUIVO_JSON}: {e}")
        return [], set()


def encontrar_proximo_id(lista_de_frases):
    """Encontra o maior ID existente e retorna o próximo ID disponível."""
    if not lista_de_frases:
        return 1
    
    max_id = 0
    for item in lista_de_frases:
        if 'id' in item and isinstance(item['id'], int) and item['id'] > max_id:
            max_id = item['id']
            
    return max_id + 1

def raspar_url(url, site_config, lista_frases, frases_set, next_id_ref):
    """Função auxiliar para raspar uma única URL."""
    
    novas_frases_nesta_pagina = 0
    
    print_url = url.split('?')[0]
    print(f"\nRaspando: {print_url}")
    
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        
        if response.status_code == 403:
            print("  Falha ao acessar o site (Status: 403 Proibido). O site está nos bloqueando.")
            return 0
        # Adicionado tratamento para 404
        if response.status_code == 404:
             print(f"  Falha ao acessar o site (Status: {response.status_code} - Página não encontrada)")
             return 0 # Indica que não encontrou frases e pode ser o fim da paginação
        if response.status_code != 200:
            print(f"  Falha ao acessar o site (Status: {response.status_code})")
            return 0

        soup = BeautifulSoup(response.content, 'html.parser')
        elementos_card = soup.select(site_config['seletor_card']) 
        
        if not elementos_card:
            print(f"  Nenhum elemento encontrado com o seletor_card: '{site_config['seletor_card']}'")
            return 0 # Retorna 0 novas frases nesta página

        print(f"  Encontrados {len(elementos_card)} elementos.")
        for card in elementos_card:
            frase_tag = card.select_one(site_config['seletor_frase'])
            
            autor_texto = "Desconhecido"
            # Verifica se o seletor_autor não é None antes de tentar usá-lo
            if site_config.get('seletor_autor'): 
                autor_tag = card.select_one(site_config['seletor_autor'])
                if autor_tag:
                    autor_texto = autor_tag.get_text().strip()
            
            if frase_tag:
                frase_texto = frase_tag.get_text(separator=' ').strip() # Usa separator=' ' para tratar <br>

                # Limpeza adicional: Remove textos muito curtos ou que parecem ser só o autor
                if frase_texto and frase_texto not in frases_set and len(frase_texto) > 10 and not frase_texto.lower().startswith("por:"):
                    # Limpa frases que são apenas citações de autor (redundante, mas seguro)
                    if frase_texto.lower().startswith("de: ") or frase_texto.lower().startswith("autor:"):
                        continue
                        
                    print(f"    + Nova frase: {frase_texto[:50]}... ({autor_texto})")
                    
                    frase_obj = {
                        "id": next_id_ref[0],
                        "frase": frase_texto,
                        "autor": autor_texto
                    }
                    
                    lista_frases.append(frase_obj)
                    frases_set.add(frase_texto)
                    next_id_ref[0] += 1 
                    novas_frases_nesta_pagina += 1
        
        return novas_frases_nesta_pagina

    except requests.exceptions.RequestException as e:
        print(f"  Erro de rede ao tentar acessar {url}: {e}")
        return 0
    except Exception as e:
        print(f"  Ocorreu um erro inesperado ao raspar {url}: {e}")
        return 0


def main():
    print("Iniciando o scraper de frases...")
    lista_de_frases, frases_existentes_set = carregar_frases_existentes()
    
    next_id = encontrar_proximo_id(lista_de_frases)
    print(f"Próximo ID a ser usado: {next_id}")
    
    next_id_referencia = [next_id]
    novas_frases_encontradas_total = 0

    for site in SITES_CONFIG:
        print(f"\n--- Processando Site: {site['nome']} ---")
        
        urls_para_visitar = []
        
        if site['tipo'] == 'blog':
            urls_para_visitar.append(site['url']) # Se for blog, só tem uma URL
            
        elif site['tipo'] == 'paginado':
            for i in range(1, site['paginas'] + 1):
                url_final = ""
                if i == 1:
                    url_final = site['url_base'] # Página 1 é sempre a base
                else:
                    # Formato /page/i (Belas Mensagens)
                    if "belasmensagens.com.br" in site['url_base']:
                        url_final = f"{site['url_base']}page/{i}" 
                    # Formato /pagina/i/ (Frases de Motivação)
                    elif "frasesdemotivacao.com.br" in site['url_base']:
                        url_final = f"{site['url_base']}pagina/{i}/"
                    # Formato /pagina/i (Frases de Inspiração)
                    elif "frasesdeinspiracao.com.br" in site['url_base']:
                         url_final = f"{site['url_base']}pagina/{i}"
                    # Formato /i/ (Frases Top) NOVO!
                    elif "frasestop.com" in site['url_base']:
                        url_final = f"{site['url_base']}{i}/" # Adiciona a barra no final
                    # Formato /i (Mundo das Mensagens, Frases do Bem)
                    elif "mundodasmensagens.com" in site['url_base'] or "frasesdobem.com.br" in site['url_base']:
                         url_final = f"{site['url_base']}{i}"
                    # Fallback genérico 
                    else:
                        # Verifica se o domínio está na lista SEM_BARRA
                        dominio_base = site['url_base'].split('/')[2] # Pega 'www.site.com'
                        if any(dominio == dominio_base for dominio in SITES_PAGINACAO_SEM_BARRA):
                            url_final = f"{site['url_base'].rstrip('/')}/{i}" # Garante que não tenha barra dupla
                        else:
                             url_final = f"{site['url_base'].rstrip('/')}/{i}/" # Garante uma barra no final
                
                urls_para_visitar.append(url_final)

        # Agora, raspe todas as URLs que encontramos
        for url in urls_para_visitar:
            novas = raspar_url(url, site, lista_de_frases, frases_existentes_set, next_id_referencia)
            # Verifica se retornou 0 E se o tipo é paginado
            if novas == 0 and site['tipo'] == 'paginado':
                print(f"  Nenhuma frase nova encontrada em {url} ou erro ao acessar. Pulando o restante das páginas para '{site['nome']}'.")
                break # Sai do loop interno (de URLs para este site)
                
            novas_frases_encontradas_total += novas
            # Pausa educada maior para evitar bloqueios
            time.sleep(1.5) 

    # Salva o arquivo JSON atualizado
    if novas_frases_encontradas_total > 0:
        print(f"\nSucesso! {novas_frases_encontradas_total} novas frases foram adicionadas.")
        
        try:
            with open(ARQUIVO_JSON, "w", encoding="utf-8") as f:
                json.dump(lista_de_frases, f, indent=4, ensure_ascii=False)
            print(f"Arquivo '{ARQUIVO_JSON}' atualizado com sucesso. Total: {len(lista_de_frases)} frases.")
        except Exception as e:
            print(f"Erro ao salvar o arquivo JSON: {e}")
            
    else:
        print("\nNenhuma frase nova encontrada nos sites especificados.")


if __name__ == "__main__":
    main()

