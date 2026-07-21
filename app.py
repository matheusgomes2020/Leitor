import streamlit as st
import pandas as pd
import re
import pytesseract
from PIL import Image

# Configuração da página
st.set_page_config(page_title="Scanner AçoNobre", page_icon="📱", layout="centered")

st.title("📱 Leitor de Produção - AçoNobre")
st.write("Tire uma foto da etiqueta para extrair o Código da Peça.")

# Botão para tirar foto com a câmara nativa
foto = st.file_uploader("📸 Clique para Tirar Foto", type=["png", "jpg", "jpeg"])

if foto is not None:
    with st.spinner("A analisar a etiqueta..."):
        try:
            # Abre a imagem
            img = Image.open(foto)
            
            # Lê o texto da imagem usando o Tesseract
            texto_lido = pytesseract.image_to_string(img)
            
            # 1. CAÇA AO CÓDIGO FILHO (A nossa prioridade máxima)
            # Procura apenas 7 números seguidos em qualquer lugar do texto
            match_codigo = re.search(r'(\d{7})', texto_lido)
            codigo_sigma = match_codigo.group(1) if match_codigo else None
            
            # 2. CAÇA AO PEDIDO (Secundário)
            match_pd = re.search(r'PD[\s:-]*(\d+)', texto_lido, re.IGNORECASE)
            pedido = match_pd.group(1) if match_pd else None
            
            # 3. EXIBIÇÃO FOCADA NO CÓDIGO
            if codigo_sigma:
                # O Pulo do Gato: formata o código para o padrão Delta/PCP
                codigo_formatado = f"{codigo_sigma[:3]}.00{codigo_sigma[3:]}"
                
                st.success("✅ Código encontrado!")
                
                # Destaque máximo para o Código Filho
                st.markdown(f"""
                <div style="background-color: #1e3d59; padding: 20px; border-radius: 10px; text-align: center;">
                    <h3 style="color: white; margin: 0;">CÓDIGO DA PEÇA</h3>
                    <h1 style="color: #ffc13b; margin: 0; font-size: 40px;">{codigo_formatado}</h1>
                </div>
                """, unsafe_allow_html=True)
                
                st.write("") # Espaçamento
                
                # Mostra o pedido apenas se o encontrar
                if pedido:
                    st.info(f"📦 **Pedido associado:** {pedido}")
                else:
                    st.warning("⚠️ **Nota:** Número do Pedido (PD) não visível na foto.")
                
                st.markdown("---")
                st.write("*(Pronto para buscar os dados desta peça no Excel do PCP...)*")
                
            else:
                st.error("❌ Não foi possível encontrar um código de 7 dígitos. Tente focar melhor a etiqueta.")
                
            # Aba de depuração para ver o que a câmara leu realmente
            with st.expander("Ver texto bruto lido pela câmara"):
                st.write(texto_lido)
                    
        except Exception as e:
            st.error(f"Erro ao processar a imagem: {e}")