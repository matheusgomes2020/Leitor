import streamlit as st
import pandas as pd
import re
import pytesseract
from PIL import Image

st.set_page_config(page_title="Scanner AçoNobre", page_icon="📱", layout="centered")
st.title("📱 Leitor de Produção - AçoNobre")
st.write("Tire uma foto da etiqueta para identificar a peça.")

foto = st.file_uploader("📸 Clique para Tirar Foto", type=["png", "jpg", "jpeg"])

if foto is not None:
    with st.spinner("A analisar a etiqueta..."):
        try:
            img = Image.open(foto)
            texto_lido = pytesseract.image_to_string(img)
            
            # 1. CAÇA AO CÓDIGO FILHO (SUPER BLINDADO: aceita ponto, vírgula, ou nada entre os números)
            # Procura o padrão: 3 números + (ponto, virgula ou espaço opcional) + 6 números
            match_filho = re.search(r'(\d{3})[.,\s]*(\d{6})', texto_lido)
            if match_filho:
                # Força a formatação perfeita: XXX.XXXXXX
                codigo_filho = f"{match_filho.group(1)}.{match_filho.group(2)}"
            else:
                codigo_filho = None
            
            # 2. CAÇA AO CÓDIGO PAI (Os 7 dígitos isolados)
            # Como o filho já foi extraído, procuramos os próximos 7 dígitos
            match_pai = re.search(r'-\s*(\d{7})\b', texto_lido)
            codigo_pai_bruto = match_pai.group(1) if match_pai else None
            
            # 3. CAÇA AO PEDIDO
            match_pd = re.search(r'PD[\s:-]*(\d+)', texto_lido, re.IGNORECASE)
            pedido = match_pd.group(1) if match_pd else None
            
            if codigo_filho:
                st.success("✅ Código da Peça lido com sucesso!")
                
                # Interface Industrial
                st.markdown(f"""
                <div style="background-color: #1e3d59; padding: 15px; border-radius: 8px; text-align: center; margin-bottom: 15px;">
                    <h4 style="color: white; margin: 0;">CÓDIGO (FILHO)</h4>
                    <h1 style="color: #ffc13b; margin: 0; font-size: 36px;">{codigo_filho}</h1>
                </div>
                """, unsafe_allow_html=True)
                
                # ==========================================
                # A MÁGICA DA BASE DE DADOS (PANDAS)
                # ==========================================
                st.write("🔍 **Buscando no sistema...**")
                
                try:
                    # Tenta carregar o Excel do PCP (Você precisa colocar o arquivo 'Lista_PCP_Global.xlsx' na mesma pasta no GitHub)
                    df_pcp = pd.read_excel("Lista_PCP_Global.xlsx", dtype=str)
                    
                    # Procura o código da peça na planilha
                    peca_info = df_pcp[df_pcp["CÓDIGO PEÇA"].str.contains(codigo_filho, na=False)]
                    
                    if not peca_info.empty:
                        desc_peca = peca_info.iloc[0]["DESCRIÇÃO PEÇA"]
                        medida = peca_info.iloc[0]["MEDIDA CORTE"]
                        espessura = peca_info.iloc[0]["ESPESSURA"]
                        
                        st.success(f"🧩 **Peça:** {desc_peca}")
                        st.info(f"📏 **Medidas:** {medida} | **Esp:** {espessura}mm")
                    else:
                        st.warning("⚠️ Código encontrado na etiqueta, mas não localizado no Excel do PCP.")
                except Exception as e:
                    st.error("⚠️ Planilha 'Lista_PCP_Global.xlsx' não encontrada no sistema. (Faça upload do Excel para o GitHub para ativar esta função).")
                # ==========================================
                
                st.markdown("---")
                if codigo_pai_bruto:
                    pai_formatado = f"{codigo_pai_bruto[:3]}.00{codigo_pai_bruto[3:]}"
                    st.write(f"🏗️ **Código Pai:** {pai_formatado}")
                if pedido:
                    st.write(f"📦 **Pedido (PD):** {pedido}")
                
            else:
                st.error("❌ O leitor não identificou um código válido. Tente melhorar o foco da câmara.")
                
            with st.expander("Ver texto bruto (Modo Técnico)"):
                st.write(texto_lido)
                    
        except Exception as e:
            st.error(f"Erro do sistema: {e}")