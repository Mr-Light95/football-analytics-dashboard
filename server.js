// Dependencies
const express = require('express');
const sql = require('mssql');
const cors = require('cors');
const { config } = require('./config');

const app = express();
const PORT = 3000;

// Middleware
app.use(cors());
app.use(express.json());

// Connect to SQL Server
let pool;
sql.connect(config).then(p => {
    pool = p;
    console.log('✅ Connected to SQL Server');
}).catch(err => {
    console.error('❌ Database connection failed:', err);
});

// ==================== API ENDPOINTS ====================

// 1. Get all branches
app.get('/api/branches', async (req, res) => {
    try {
        const result = await pool.request().query('SELECT * FROM Branches');
        res.json(result.recordset);
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
});

// 2. Get all players (with optional filters)
app.get('/api/players', async (req, res) => {
    try {
        const { branchId, rankId } = req.query;

        let query = `
            SELECT p.*, b.BranchName, r.RankName 
            FROM Players p
            LEFT JOIN Branches b ON p.BranchID = b.BranchID
            LEFT JOIN Ranks r ON p.RankID = r.RankID
            WHERE 1=1
        `;

        if (branchId) query += ` AND p.BranchID = ${branchId}`;
        if (rankId) query += ` AND p.RankID = ${rankId}`;

        const result = await pool.request().query(query);
        res.json(result.recordset);
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
});

// 3. Get all games
app.get('/api/games', async (req, res) => {
    try {
        const { branchId, season } = req.query;

        let query = 'SELECT * FROM Games WHERE 1=1';
        if (branchId) query += ` AND BranchID = ${branchId}`;
        if (season) query += ` AND Season = '${season}'`;

        const result = await pool.request().query(query);
        res.json(result.recordset);
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
});

// 4. Get income data
app.get('/api/incomes', async (req, res) => {
    try {
        const { branchId } = req.query;

        let query = 'SELECT * FROM Incomes WHERE 1=1';
        if (branchId) query += ` AND BranchID = ${branchId}`;

        const result = await pool.request().query(query);
        res.json(result.recordset);
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
});

// 5. Get ranks
app.get('/api/ranks', async (req, res) => {
    try {
        const result = await pool.request().query('SELECT * FROM Ranks ORDER BY Level');
        res.json(result.recordset);
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
});

// 6. Get aggregated statistics
app.get('/api/stats/summary', async (req, res) => {
    try {
        const stats = {};

        // Total players
        const playersResult = await pool.request().query('SELECT COUNT(*) as count FROM Players');
        stats.totalPlayers = playersResult.recordset[0].count;

        // Total games
        const gamesResult = await pool.request().query('SELECT COUNT(*) as count FROM Games');
        stats.totalGames = gamesResult.recordset[0].count;

        // Total income
        const incomeResult = await pool.request().query('SELECT SUM(Amount) as total FROM Incomes');
        stats.totalIncome = incomeResult.recordset[0].total;

        // Win rate
        const winsResult = await pool.request().query(`
            SELECT 
                CAST(SUM(CASE WHEN Result = 'Win' THEN 1 ELSE 0 END) AS FLOAT) / COUNT(*) * 100 as winRate
            FROM Games
        `);
        stats.winRate = winsResult.recordset[0].winRate;

        res.json(stats);
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
});

// 7. Income by branch
app.get('/api/analytics/income-by-branch', async (req, res) => {
    try {
        const result = await pool.request().query(`
            SELECT 
                b.BranchName,
                SUM(i.Amount) as TotalIncome
            FROM Incomes i
            JOIN Branches b ON i.BranchID = b.BranchID
            GROUP BY b.BranchName
            ORDER BY TotalIncome DESC
        `);
        res.json(result.recordset);
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
});

// 8. Players by position
app.get('/api/analytics/players-by-position', async (req, res) => {
    try {
        const result = await pool.request().query(`
            SELECT 
                Position,
                COUNT(*) as Count
            FROM Players
            GROUP BY Position
        `);
        res.json(result.recordset);
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
});

// 9. Players by rank
app.get('/api/analytics/players-by-rank', async (req, res) => {
    try {
        const result = await pool.request().query(`
            SELECT 
                r.RankName,
                COUNT(p.PlayerID) as Count
            FROM Ranks r
            LEFT JOIN Players p ON r.RankID = p.RankID
            GROUP BY r.RankName, r.Level
            ORDER BY r.Level
        `);
        res.json(result.recordset);
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
});

// 10. Top players by salary
app.get('/api/analytics/top-players', async (req, res) => {
    try {
        const limit = req.query.limit || 10;
        const result = await pool.request().query(`
            SELECT TOP ${limit}
                PlayerName,
                Position,
                Salary,
                Nationality
            FROM Players
            ORDER BY Salary DESC
        `);
        res.json(result.recordset);
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
});
async function loadPlayers() {
    try {
        const res = await fetch(`${API_URL}/players`);
        const players = await res.json();

        const grid = document.getElementById('playersGrid');
        grid.innerHTML = '';

        players.forEach(p => {
            const card = document.createElement('div');
            card.className = 'player-card';

            card.innerHTML = `
                <img src="${p.PhotoUrl || 'https://via.placeholder.com/150'}">
                <div class="player-name">${p.PlayerName}</div>
                <div class="player-position">${p.Position || ''}</div>
                <div class="player-stats">
                    ⭐ Rank: ${p.RankName}<br>
                    🎂 Age: ${p.Age}<br>
                    💷 Salary: £${(p.Salary / 1_000_000).toFixed(1)}M<br>
                    🏟️ Branch: ${p.BranchName}
                </div>
            `;

            // CLICK (important for next steps)
            card.onclick = () => selectPlayer(p);

            grid.appendChild(card);
        });

    } catch (err) {
        console.error('Error loading players:', err);
    }
}
function selectPlayer(player) {
    alert(`⚽ ${player.PlayerName} selected!\nNext step: animation 😉`);
}
async function initDashboard() {
    await loadFilters();
    await loadData();
    await loadPlayers();   // 👈 ADD THIS
}


// Start server
app.listen(PORT, () => {
    console.log(`🚀 Server running on http://localhost:${PORT}`);
});