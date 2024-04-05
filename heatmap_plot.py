import os
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Caminho da pasta com os arquivos CSV
folder_path = '/Users/carnotbraun/tese-mestrado/simu/data/rsus_most_csv'

# Lista para armazenar os DataFrames de cada arquivo
dfs = []

# Itera sobre todos os arquivos na pasta
for filename in os.listdir(folder_path):
    if filename.endswith('.csv'):
        file_path = os.path.join(folder_path, filename)
        # Obtém o rsu_id a partir do nome do arquivo
        rsu_id = filename.split('_')[-1].split('.')[0]
        # Lê o arquivo CSV e adiciona ao DataFrame
        df = pd.read_csv(file_path, sep=',', header=0)
        # Adiciona uma coluna 'rsu_id' com o ID da RSU
        df['rsu_id'] = rsu_id
        dfs.append(df)

# Concatena todos os DataFrames em um único DataFrame
merged_df = pd.concat(dfs)

# Pivotando o DataFrame pelo rsu_id
# Não esquecer que a antiga base de dados era c02 não co2
pivot_df = merged_df.pivot_table(index='rsu_id', columns='step', values='c02_emission', aggfunc='sum')

# Transpondo o DataFrame
pivot_df_transposed = pivot_df.T

# Cria o heatmap sem legenda e números de passo no eixo y
plt.figure(figsize=(10, 8))
ax = sns.heatmap(pivot_df_transposed, cmap='gnuplot_r')
ax.set_yticks([])
ax.set_xticks([])
plt.title('MoST Co2 Emission')
plt.savefig('Co2_heatmap')
plt.show()
