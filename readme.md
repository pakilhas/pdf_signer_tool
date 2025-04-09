# PDF Signer Tool - Assinatura Digital de PDFs

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![Django](https://img.shields.io/badge/Django-5.1-green)
![AWS](https://img.shields.io/badge/Hosted%20on-AWS%20EC2-orange)

## 📌 Sobre o Projeto

Aplicação web desenvolvida em Python/Django para adicionar assinaturas digitais em documentos PDF de forma automatizada.

🔗 **Acesso Online:** [http://3.12.148.70/](http://3.12.148.70/)

## ✨ Funcionalidades

- 📤 Upload de arquivos PDF
- 🖼️ Upload de imagens de assinatura (PNG/JPG)
- ⚡ Processamento automático em todas as páginas
- 📥 Download do documento assinado
- 🖌️ Posicionamento no canto inferior direito

## 🛠️ Tecnologias Utilizadas

| Tecnologia | Finalidade |
|------------|------------|
| Python 3.10+ | Lógica principal |
| Django 5.1 | Framework web |
| PyPDF2 | Manipulação de PDF |
| ReportLab | Geração de PDFs |
| Pillow | Processamento de imagens |
| AWS EC2 | Hospedagem em nuvem |
| Nginx | Servidor web |
| Gunicorn | Servidor de aplicação |

## 🚀 Como Funciona

1. Usuário faz upload de:
   - Documento PDF
   - Imagem de assinatura
2. Sistema processa:
   - Adiciona assinatura em todas páginas
   - Posiciona no canto inferior direito
3. Usuário recebe:
   - PDF assinado para download



## ☁️ Implantação na AWS EC2

Configuração do Servidor:

    Ubuntu 22.04 LTS

    Nginx como proxy reverso

    Gunicorn como servidor WSGI

    PostgreSQL para banco de dados

Acesso Online:
🔗 http://3.12.148.70/
