import streamlit as st
import pandas as pd
import re
import pytesseract
from PIL import Image

# Configuração da página
st.set_page_config(page_title="Scanner AçoNobre", page_icon="📱", layout="centered")

st.title("📱 Leitor de Produção - AçoNobre")
st.write("Tire uma foto da etiqueta para leitura.")

# Usa o uploader para acionar a câmara nativa do telemóvel (com foco e zoom)
foto = st.file_uploader("📸 Clique para Tirar Foto", type=["png", "jpg", "jpeg"])

if foto is not None:
    with st.spinner("A analisar a etiqueta..."):
        try:
            # Abre a imagem
            img = Image.open(foto)
            
            # Lê o texto da imagem usando o Tesseract
            texto_lido = pytesseract.image_to_string(img)
            
            # ==========================================
            # REGRA BLINDADA PARA LER O PEDIDO
            # Aceita PD:, PD-, PD_ ou só PD seguido do número
            # ==========================================
            match_pd = re.search(r'PD[\s:-]*(\d+)', texto_lido, re.IGNORECASE)
            pedido = match_pd.group(1) if match_pd else None
            
            # Busca o código do SigmaNest
            match_codigo = re.search(r'-\s*(\d{7})', texto_lido)
            codigo_sigma = match_codigo.group(1) if match_codigo else None
            
            if pedido and codigo_sigma:
                # O Pulo do Gato: Corrige a formatação do SigmaNest (ex: 8092177 -> 809.002177)
                codigo_formatado = f"{codigo_sigma[:3]}.00{codigo_sigma[3:]}"
                
                st.success("✅ Etiqueta Lida com Sucesso!")
                
                # Exibe os dados extraídos
                st.info(f"📦 **PEDIDO:** {pedido}")
                st.info(f"⚙️ **CÓDIGO (Delta/PCP):** {codigo_formatado}")
                
                # Espaço reservado para o futuro cruzamento com o Excel
                st.markdown("---")
                st.write("*(Na próxima fase, o sistema vai procurar este código na Lista Global do PCP e mostrar o **Item Pai** aqui!)*")
                
            else:
                st.error("❌ Não foi possível extrair os dados. Tente focar melhor a câmara.")
            
            # Deixa sempre a opção de ver o texto sujo para podermos corrigir erros no futuro
            with st.expander("Ver texto bruto lido pela câmara"):
                st.write(texto_lido)
                    
        except Exception as e:
            st.error(f"Erro ao processar a imagem: {e}")