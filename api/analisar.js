import { Groq } from 'groq-sdk';
import dotenv from 'dotenv';

dotenv.config();

const groq = new Groq({
    apiKey: process.env.GROQ_API_KEY,
});

// Banco de dados simulado em memória (Temporário para a sessão da Serverless Function)
let bancoClientesSimulado = {
    "1": { nome: "Mariana Silva", idade: 34, renda: 18000, score: 890, valor: 120000, status: "APROVADO" }
};

export default async function handler(req, res) {
    res.setHeader('Access-Control-Allow-Credentials', true);
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET,OPTIONS,PATCH,DELETE,POST,PUT');
    res.setHeader('Access-Control-Allow-Headers', 'X-CSRF-Token, X-Requested-With, Accept, Accept-Version, Content-Length, Content-MD5, Content-Type, Date, X-Api-Version');

    if (req.method === 'OPTIONS') {
        return res.status(200).end();
    }

    const { method } = req;
    const { id } = req.query; // Utilizado para READ individual, UPDATE e DELETE

    try {
        // -----------------------------------------------------------------
        // [C]RUD - CREATE (POST) -> Envia uma nova proposta para a IA avaliar e cadastrar
        // -----------------------------------------------------------------
        if (method === 'POST') {
            const { nome, idade, renda, score, valor } = req.body || req.query;
            
            const promptApi = `Aja como o motor de risco de crédito de uma Fintech. Analise: Cliente: ${nome}, Idade: ${idade}, Renda: ${renda}, Score: ${score}, Valor: ${valor}. Responda em JSON rigoroso com as chaves: "status", "taxa_juros_anual" e "justificativa".`;
            
            const completion = await groq.chat.completions.create({
                messages: [{ role: 'user', content: promptApi }],
                model: 'llama-3.1-8b-instant',
                temperature: 0.1,
                response_format: { type: 'json_object' }
            });

            const resultadoIa = JSON.parse(completion.choices[0].message.content);
            const novoId = String(Object.keys(bancoClientesSimulado).length + 1);
            
            // Salva no banco de dados simulado
            bancoClientesSimulado[novoId] = { nome, idade, renda, score, valor, ...resultadoIa };

            return res.status(201).json({
                mensagem: "🎉 [CREATE] Proposta criada e avaliada com sucesso!",
                id: novoId,
                dados: bancoClientesSimulado[novoId]
            });
        }

        // -----------------------------------------------------------------
        // C[R]UD - READ (GET) -> Retorna a lista completa ou um cliente específico
        // -----------------------------------------------------------------
        if (method === 'GET') {
            if (id) {
                if (!bancoClientesSimulado[id]) return res.status(404).json({ erro: "Cliente não encontrado" });
                return res.status(200).json({ mensagem: "📖 [READ] Registro localizado!", dados: bancoClientesSimulado[id] });
            }
            return res.status(200).json({ mensagem: "📖 [READ] Listando todos os registros!", banco: bancoClientesSimulado });
        }

        // -----------------------------------------------------------------
        // CR[U]D - UPDATE (PUT) -> Atualiza dados cadastrais de um ID existente
        // -----------------------------------------------------------------
        if (method === 'PUT') {
            if (!id || !bancoClientesSimulado[id]) return res.status(404).json({ erro: "ID inválido para atualização" });
            
            const corpo = req.body || req.query;
            bancoClientesSimulado[id].nome = corpo.nome || bancoClientesSimulado[id].nome;
            bancoClientesSimulado[id].renda = corpo.renda || bancoClientesSimulado[id].renda;
            
            return res.status(200).json({
                mensagem: `🔄 [UPDATE] Registro ID ${id} atualizado com sucesso!`,
                dados: bancoClientesSimulado[id]
            });
        }

        // -----------------------------------------------------------------
        // CRU[D] - DELETE (DELETE) -> Remove uma proposta do sistema
        // -----------------------------------------------------------------
        if (method === 'DELETE') {
            if (!id || !bancoClientesSimulado[id]) return res.status(404).json({ erro: "ID inválido para exclusão" });
            
            delete bancoClientesSimulado[id];
            return res.status(200).json({ mensagem: `🗑️ [DELETE] Registro ID ${id} foi removido do sistema.` });
        }

        return res.status(451).json({ erro: "Método HTTP não suportado nesta rota." });

    } catch (error) {
        return res.status(500).json({ error: error.message });
    }
}