import { Groq } from 'groq-sdk';
import dotenv from 'dotenv';

dotenv.config();

// Inicializa o cliente do Groq de forma segura
const groq = new Groq({
    apiKey: process.env.GROQ_API_KEY,
});

export default async function handler(req, res) {
    // Permite que o script do aluno ou o Front-end acessem a API sem erros de CORS
    res.setHeader('Access-Control-Allow-Credentials', true);
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET,OPTIONS,PATCH,DELETE,POST,PUT');
    res.setHeader('Access-Control-Allow-Headers', 'X-CSRF-Token, X-Requested-With, Accept, Accept-Version, Content-Length, Content-MD5, Content-Type, Date, X-Api-Version');

    if (req.method === 'OPTIONS') {
        return res.status(200).end();
    }

    try {
        // Captura os dados enviados via query string (?nome=...&idade=...)
        const { nome, idade, renda, score, valor } = req.query;

        const promptApi = `
        Aja como o motor de análise de risco de crédito de uma Fintech.
        Analise o seguinte perfil de forma estrita:
        - Cliente: ${nome || 'Cliente API'}
        - Idade: ${idade || '30'} anos
        - Renda Mensal: R$ ${renda || '5000'}
        - Score de Crédito Serasa: ${score || '500'}
        - Valor do Empréstimo Solicitado: R$ ${valor || '10000'}
        
        Responda de forma direta e estritamente em JSON válido.
        O formato JSON deve conter exatamente as chaves com aspas duplas: "status" (APROVADO ou REPROVADO), "taxa_juros_anual" (ex: "12%") e "justificativa" (máximo 10 palavras).
        `;

        const completion = await groq.chat.completions.create({
            messages: [{ role: 'user', content: promptApi }],
            model: 'llama-3.1-8b-instant',
            temperature: 0.1,
            max_tokens: 100,
            response_format: { type: 'json_object' }
        });

        const respostaIa = JSON.parse(completion.choices[0].message.content);

        // DEVOLVE JSON PURO E REAL! Sem HTML em volta, sem bugs de parse!
        return res.status(200).json(respostaIa);

    } catch (error) {
        return res.status(500).json({ error: error.message });
    }
}