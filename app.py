import streamlit as st
import pandas as pd
import re
import pytesseract
from PIL import Image

# Configuração da página
st.set_page_config(page_title="Scanner AçoNobre", page_icon="📱", layout="centered")
st.title("📱 Leitor de Produção - AçoNobre")
st.write("Tire uma foto da etiqueta para identificar a peça.")

foto = st.file_uploader("📸 Clique para Tirar Foto", type=["png", "jpg", "jpeg"])

if foto is not None:
    with st.spinner("A analisar a etiqueta..."):
        try:
            img = Image.open(foto)
            texto_lido = pytesseract.image_to_string(img)
            
            # 1. CAÇA AO CÓDIGO FILHO (Ex: 902.000769)
            match_filho = re.search(r'(\d{3})[.,\s]*(\d{6})', texto_lido)
            codigo_filho = f"{match_filho.group(1)}.{match_filho.group(2)}" if match_filho else None
            
            # 2. CAÇA AO CÓDIGO PAI (Ex: 8090768 - O SigmaNest corta os dois zeros)
            match_pai = re.search(r'-\s*(\d{7})\b', texto_lido)
            codigo_pai_bruto = match_pai.group(1) if match_pai else None
            
            # 3. CAÇA AO PEDIDO
            match_pd = re.search(r'PD[\s:-]*(\d+)', texto_lido, re.IGNORECASE)
            pedido = match_pd.group(1) if match_pd else None
            
            # 4. CAÇA AO CLIENTE (Lê o que está logo abaixo ou à frente de "Cliente:")
            match_cliente = re.search(r'Cliente:[\s\n]*([A-Za-zÀ-ÖØ-öø-ÿ0-9\s]+?)(?=\n|Dimensões|Qtde)', texto_lido, re.IGNORECASE)
            cliente = match_cliente.group(1).strip() if match_cliente else None

            # LÓGICA DE EXIBIÇÃO
            if codigo_filho or pedido:
                st.success("✅ Leitura Concluída!")
                
                if codigo_filho:
                    st.markdown(f"""
                    <div style="background-color: #1e3d59; padding: 15px; border-radius: 8px; text-align: center; margin-bottom: 15px;">
                        <h4 style="color: white; margin: 0;">CÓDIGO (FILHO)</h4>
                        <h1 style="color: #ffc13b; margin: 0; font-size: 36px;">{codigo_filho}</h1>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # BUSCA NO EXCEL DO PCP
                    st.write("🔍 **Buscando no sistema...**")
                    try:
                        df_pcp = pd.read_excel("Lista_PCP_Global.xlsx", dtype=str)
                        peca_info = df_pcp[df_pcp["CÓDIGO PEÇA"].str.contains(codigo_filho, na=False)]
                        
                        if not peca_info.empty:
                            desc_peca = peca_info.iloc[0]["DESCRIÇÃO PEÇA"]
                            medida = peca_info.iloc[0]["MEDIDA CORTE"]
                            espessura = peca_info.iloc[0]["ESPESSURA"]
                            
                            st.success(f"🧩 **Peça:** {desc_peca}")
                            st.info(f"📏 **Medidas:** {medida} | **Esp:** {espessura}mm")
                        else:
                            st.warning("⚠️ Código encontrado, mas não localizado no Excel do PCP.")
                    except Exception:
                        st.error("⚠️ Planilha 'Lista_PCP_Global.xlsx' não encontrada no sistema.")
                        
                else:
                    st.warning("⚠️ O Código da Peça não foi lido pelo leitor ótico.")
                
                st.markdown("---")
                
                # Exibe o Cliente se achou
                if cliente:
                    st.write(f"🏢 **Cliente:** {cliente}")
                
                # Devolve os dois zeros (.00) ao Código Pai
                if codigo_pai_bruto:
                    pai_formatado = f"{codigo_pai_bruto[:3]}.00{codigo_pai_bruto[3:]}"
                    st.write(f"🏗️ **Código Pai:** {pai_formatado}")
                
                if pedido:
                    st.write(f"📦 **Pedido (PD):** {pedido}")
                    
            else:
                st.error("❌ O leitor não identificou nem o Código nem o Pedido.")
                
            with st.expander("Ver texto bruto (Modo Técnico)"):
                st.write(texto_lido)
                    
        except Exception as e:
            st.error(f"Erro do sistema: {e}")