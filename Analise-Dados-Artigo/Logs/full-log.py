import re
import csv
import argparse

def parse_log_file(log_file, csv_file):
    # Expressão regular para extrair os valores de tempo e os nomes das tabelas das entradas de log
    log_pattern = re.compile(r'Migration of Table:(\w+) is (\d+\.\d+) seconds')

    # Lista para armazenar os dados extraídos
    log_data = []

    # Ler o arquivo de log e extrair os valores de tempo e nomes das tabelas
    try:
        with open(log_file, 'r') as file:
            for line in file:
                match = log_pattern.search(line)
                if match:
                    table_name, time_elapsed = match.groups()
                    log_data.append([table_name, float(time_elapsed)])
    except FileNotFoundError:
        print(f"Erro: O arquivo '{log_file}' não foi encontrado.")
        return

    # Escrever os dados extraídos em um arquivo CSV
    with open(csv_file, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Table Name', 'Time Elapsed (seconds)'])
        writer.writerows(log_data)

    print(f"Dados extraídos e salvos em {csv_file}")

def main():
    # Configurar o argparse
    parser = argparse.ArgumentParser(description='Extrair nomes de tabelas e valores de tempo de logs e salvar em um arquivo CSV.')
    parser.add_argument('log_file', type=str, help='Nome do arquivo de log de entrada.')
    parser.add_argument('csv_file', type=str, help='Nome do arquivo CSV de saída.')

    args = parser.parse_args()

    # Chamar a função para processar o arquivo de log e salvar no CSV
    parse_log_file(args.log_file, args.csv_file)

if __name__ == "__main__":
    main()
