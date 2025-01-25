import os
import requests
import tempfile
import subprocess
import json
import sys

# coloque aqui o seu token do pool
pooltoken = ""

#coloque aqui quantsa threads deseja usar no keyhunt
numthreads = 6

#endereço da carteira bitcoin do premio do desafio
target_address = "1BY8GQbnueYofwSuFAT3USAhGjPrkxDdW9"

#arquivos
pool_file = "pool.txt"
key_file = "KEYFOUNDKEYFOUND.txt"



def call_api():
    url = "https://bitcoinflix.replit.app/api/block"
    headers = {
        "pool-token": f"{pooltoken}"
    }

    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()

            # Exibindo os resultados
            print("ID:", data.get("id"))
            print("Position:", data.get("position"))
            print("Status:", data.get("status"))
            print("Range Start:", data.get("range", {}).get("start"))
            print("Range End:", data.get("range", {}).get("end"))
            #print("Checkwork Addresses:", data.get("checkwork_addresses", []))
            print("Message:", data.get("message"))


            return data
        else:
            print(f"Erro: Status code {response.status_code}")
            print("Detalhes:", response.text)
            return None
    except Exception as e:
        print(f"Ocorreu um erro: {e}")
        return None


def write_pool_file(checkwork_addresses):
    checkwork_addresses.append(f"{target_address}")
    with open(pool_file, 'w') as f:
        for address in checkwork_addresses:
            f.write(address + "\n")
    return pool_file


def run_keyhunt(pool_file, range_start, range_end):
    try:
        command = ["./keyhunt", "-f", pool_file, "-r", f"{range_start}:{range_end}", "-q", "-l" , "compress" , "-s", "0", "-t", f"{numthreads}", "-n", "1024"]

        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Erro ao executar o programa externo: {e}")


def process_found_keys():
    key_file = "KEYFOUNDKEYFOUND.txt"
    if not os.path.exists(key_file):
        print(f"Arquivo {key_file} não encontrado.")
        return ""

    address_key_map = {}

    with open(key_file, 'r') as f:
        lines = f.readlines()
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            if line.startswith("Private Key:"):
                # Obter a Private Key
                private_key = line.split(":")[1].strip() if ":" in line else None

                address_key_map[i] = private_key

                # Avançar para o próximo bloco
                i += 3
            else:
                # Continuar para a próxima linha
                i += 1

    # Formatar até 10 chaves privadas com zeros à esquerda
    private_keys = [
        f"0x{'0' * (64 - len(key))}{key}" for key in list(address_key_map.values())[:10]
    ]

    # Criar o objeto JSON formatado
    result = {
        "privateKeys": private_keys
    }


    return result  




def post_keys(private_keys):
    url = "https://bitcoinflix.replit.app/api/block"
    headers = {
        "pool-token": f"{pooltoken}",
        "Content-Type": "application/json"
    }
    payload = private_keys

    try:
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                os.system('clear')
                print("Chaves enviadas com sucesso!")
            else:
                print("Erro na resposta da API:", result)
        else:
            print(f"Erro na requisição POST: Status code {response.status_code}")
            #sys.exit(0)
    except Exception as e:
        print(f"Erro ao enviar os dados: {e}")


def clean_up(files):
    for file in files:
        if os.path.exists(file):
            old_file = f"{file}.OLD"

            # Verificar se já existe um arquivo .OLD
            if os.path.exists(old_file):
                try:
                    os.remove(old_file)  # Remover o arquivo existente .OLD
                    #print(f"Arquivo {old_file} removido.")
                except Exception as e:
                    print(f"Erro ao remover {old_file}: {e}")

            # Renomear o arquivo original para .OLD
            try:
                os.rename(file, old_file)
                #print(f"Arquivo {file} renomeado para {old_file}.")
            except Exception as e:
                print(f"Erro ao renomear {file}: {e}")


def check_wallet_found():
    if not os.path.exists(key_file):
        print(f"Arquivo {key_file} não encontrado.")
        return False

    with open(key_file, 'r') as f:
        lines = f.readlines()
        for line in lines:
            if target_address in line:
                print(f"************************************************")
                print(f"Carteira {target_address} encontrada no arquivo!")
                print(f"************************************************")
                sys.exit(0)  # Termina a execução imediatamente

    #print(f"Carteira {target_address} não encontrada no arquivo.")
    return False


def main():
    
    os.system('clear')
    print(f"Auto Pool 67 v1.0")
    print(f"Economizei seu tempo ? mande um cafezinho :-) Rede LN neutraldenim21@walletofsatoshi.com")
    
    while True:
      

        print(f"---------------------------------------------------------------------------------")

        #limpa qualquer lixo
        clean_up([f"{key_file}", f"{pool_file}"])

        data = call_api()
        if not data:
            break

        range_start = data.get("range", {}).get("start")[2:]
        range_end = data.get("range", {}).get("end")[2:]
        checkwork_addresses = data.get("checkwork_addresses", [])

        if not (range_start and range_end and checkwork_addresses):
            print("Dados insuficientes para continuar.")
            break

        write_pool_file(checkwork_addresses)
        run_keyhunt(pool_file, range_start, range_end)

        check_wallet_found()

        private_keys = process_found_keys()

        post_keys(private_keys)




if __name__ == "__main__":
    main()
