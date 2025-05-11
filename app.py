import streamlit as st
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

#conecta ao banco SQLite
con = sqlite3.connect("company.db")
cur = con.cursor()

st.title("Workers Dashboard")

#cargos distintos
cur.execute("SELECT DISTINCT REPLACE(cargo, 'Desenvolvedora', 'Desenvolvedor') AS cargo FROM workers ORDER BY REPLACE(cargo, 'Desenvolvedora', 'Desenvolvedor')") # o REPLACE serve para unificar Desenvolvedor e Desenvolvedora como o mesmo cargo
cargos = cur.fetchall()
df = pd.DataFrame(cargos, columns=["Cargo"])

st.subheader("Total de cargos distintos")
st.markdown(f"<h3>{len(df)}</h3>", unsafe_allow_html=True)

st.subheader("Cargos distintos")
df = df.sort_values("Cargo")
df.index = df.index + 1 #para que o índice não comece em 0
st.dataframe(df)



#top 5 maiores salários
st.subheader("Top 5 maiores salários")
cur.execute("SELECT nome, cargo, salario FROM workers ORDER BY salario DESC LIMIT 5")
dados = cur.fetchall()
df_maiores = pd.DataFrame(dados, columns=["Nome", "Cargo", "Salário"])
df_maiores.index = df_maiores.index + 1
st.dataframe(df_maiores)

#plot do gráfico
fig, ax = plt.subplots()
df_maiores_sorted = df_maiores.sort_values("Salário", ascending=False)
bars = ax.bar(df_maiores_sorted["Nome"], df_maiores_sorted["Salário"], color="#4169e1")
ax.set_ylabel("Salário")
ax.set_title("Top 5 maiores salários")
for bar in bars: #para exibir o valor do salário acima da barra
    height = bar.get_height()
    ax.text(
        bar.get_x() + bar.get_width() / 2,  
        height,                             
        f"{height:,.0f}",                   
        ha="center", va="bottom", fontsize=9
    )
st.pyplot(fig)

#top 5 menores salários
st.subheader("Top 5 menores salários")
cur.execute("SELECT nome, cargo, salario FROM workers ORDER BY salario ASC LIMIT 5")
dados = cur.fetchall()
df_menores = pd.DataFrame(dados, columns=["Nome", "Cargo", "Salário"])
df_menores.index = df_menores.index + 1 
st.dataframe(df_menores)

#plot do gráfico
fig, ax = plt.subplots()
df_menores_sorted = df_menores.sort_values("Salário")
bars = ax.bar(df_menores_sorted["Nome"], df_menores_sorted["Salário"], color="#ADD8E6")
ax.set_ylabel("Salário")
ax.set_title("Top 5 menores salários")
for bar in bars:
    height = bar.get_height()
    ax.text(
        bar.get_x() + bar.get_width() / 2,  
        height,                             
        f"{height:,.0f}",               
        ha="center", va="bottom", fontsize=9
    )
st.pyplot(fig)

#gráfico combinado top 5 maiores e menores
st.subheader("Top 5 maiores e menores salários (comparativo)")
df_comb = pd.concat([df_maiores, df_menores]).sort_values("Salário", ascending=False)
cores = ["#1f77b4" if salario in df_maiores["Salário"].values else "#ADD8E6" for salario in df_comb["Salário"]]
fig, ax = plt.subplots()
bars = ax.bar(df_comb["Nome"], df_comb["Salário"], color=cores)
ax.set_ylabel("Salário")
ax.set_title("Top 5 maiores e menores salários")
for bar in bars:
    height = bar.get_height()
    ax.text(
        bar.get_x() + bar.get_width() / 2,
        height,
        f"{height:,.0f}",
        ha="center", va="bottom", fontsize=9
    )
st.pyplot(fig)

#média salarial por cargo
st.subheader("Média salarial por cargo")
cur.execute("""
    SELECT REPLACE(cargo, 'Desenvolvedora', 'Desenvolvedor') AS cargo, ROUND(AVG(salario), 2) as media
    FROM workers
    GROUP BY REPLACE(cargo, 'Desenvolvedora', 'Desenvolvedor')
    ORDER BY media DESC
""")
dados = cur.fetchall()
df_media = pd.DataFrame(dados, columns=["Cargo", "Média Salarial"])
df_media.index = df_media.index + 1
df_media["Média Salarial"] = df_media["Média Salarial"].round(0)
st.dataframe(df_media)
#plot do gráfico
fig, ax = plt.subplots(figsize=(10, 6))
df_sorted = df_media.sort_values("Média Salarial")
bars = ax.bar(df_sorted["Cargo"], df_sorted["Média Salarial"], color="purple")
ax.set_ylabel("Média Salarial")
ax.set_title("Média salarial por cargo")
ax.set_xticklabels(df_sorted["Cargo"], rotation=45, ha="right")
for bar in bars:
    height = bar.get_height()
    ax.text(
        bar.get_x() + bar.get_width() / 2,
        height,
        f"{height:,.0f}",
        ha="center", va="bottom", fontsize=9
    )
st.pyplot(fig)

#maiores salários por cargo
st.subheader("Maiores salários por cargo")
cur.execute("""
    WITH normalizados AS (
        SELECT nome, salario,
               REPLACE(cargo, 'Desenvolvedora', 'Desenvolvedor') AS cargo_normalizado
        FROM workers
    ),
    maiores AS (
        SELECT cargo_normalizado, MAX(salario) AS max_sal
        FROM normalizados
        GROUP BY cargo_normalizado
    )
    SELECT n.nome, n.salario, n.cargo_normalizado AS cargo
    FROM normalizados n
    INNER JOIN maiores m
      ON n.cargo_normalizado = m.cargo_normalizado
     AND n.salario = m.max_sal
    ORDER BY n.salario DESC
""")
dados = cur.fetchall()
df_max_cargo = pd.DataFrame(dados, columns=["Nome", "Salário", "Cargo"])
df_max_cargo.index = df_max_cargo.index + 1
st.dataframe(df_max_cargo)

#botão interativo
modo = st.radio("Exibir gráfico por:", ["Nome", "Cargo"])

fig, ax = plt.subplots(figsize=(10, 6))

#plota condicionalmente a partir do valor do botão
if modo == "Nome":
    nomes_agrupados = df_max_cargo.groupby("Cargo")["Nome"].apply(lambda x: "/".join(x)).reset_index()
    df_plot = df_max_cargo.merge(nomes_agrupados, on="Cargo")
    df_plot = df_plot.drop_duplicates(subset=["Cargo"])
    df_plot = df_plot.sort_values("Salário", ascending=False)

    bars = ax.bar(df_plot["Nome_y"], df_plot["Salário"], color="orange")
    ax.set_xlabel("Nome")
    ax.set_title("Maiores salários por cargo (nomes)")

    ax.set_xticklabels(df_plot["Nome_y"], rotation=45, ha="right")

else:
    df_plot = df_max_cargo.groupby("Cargo").max().reset_index()
    df_plot = df_plot.sort_values("Salário", ascending=False)

    bars = ax.bar(df_plot["Cargo"], df_plot["Salário"], color="orange")
    ax.set_xlabel("Cargo")
    ax.set_title("Maiores salários por cargo")

    ax.set_xticklabels(df_plot["Cargo"], rotation=45, ha="right")

#adiciona os valores acima das barras
for bar in bars:
    height = bar.get_height()
    ax.text(
        bar.get_x() + bar.get_width() / 2,
        height,
        f"{height:,.0f}",
        ha="center", va="bottom", fontsize=9
    )

ax.set_ylabel("Salário")
st.pyplot(fig)

#fecha a conexão
con.close()
