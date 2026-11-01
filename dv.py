from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import pyodbc
from datetime import datetime

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend communication

# SQL Server Configuration
DB_CONFIG = {
    'server': r'(localdb)\MSSQLLocalDB',  # or just 'localhost'
    'database': 'PremierLeagueClub',
    'trusted_connection': 'yes',  # Use Windows Authentication
    'driver': '{ODBC Driver 17 for SQL Server}'
}

def get_db_connection():
    """Create database connection"""
    try:
        conn_str = (
            f"DRIVER={DB_CONFIG['driver']};"
            f"SERVER={DB_CONFIG['server']};"
            f"DATABASE={DB_CONFIG['database']};"
            f"Trusted_Connection=yes;"  # Windows Authentication
        )
        conn = pyodbc.connect(conn_str)
        return conn
    except Exception as e:
        print(f"❌ Database connection error: {e}")
        return None

# ==================== SERVE DASHBOARD ====================
@app.route('/')
def serve_dashboard():
    """Serve the main dashboard HTML"""
    return send_from_directory('.', 'index.html')

# ==================== API ENDPOINTS ====================

@app.route('/api/health', methods=['GET'])
def health_check():
    """Check if API is running"""
    return jsonify({
        'status': 'healthy',
        'message': 'Premier League Dashboard API is running',
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    })

@app.route('/api/branches', methods=['GET'])
def get_branches():
    """Get all branches"""
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({'error': 'Database connection failed'}), 500
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Branches")
        columns = [column[0] for column in cursor.description]
        results = []
        
        for row in cursor.fetchall():
            results.append(dict(zip(columns, row)))
        
        conn.close()
        return jsonify(results)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/ranks', methods=['GET'])
def get_ranks():
    """Get all ranks"""
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({'error': 'Database connection failed'}), 500
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM Ranks ORDER BY Level")
        columns = [column[0] for column in cursor.description]
        results = []
        
        for row in cursor.fetchall():
            results.append(dict(zip(columns, row)))
        
        conn.close()
        return jsonify(results)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/players', methods=['GET'])
def get_players():
    """Get all players with optional filters"""
    try:
        branch_id = request.args.get('branchId')
        rank_id = request.args.get('rankId')
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = """
            SELECT p.*, b.BranchName, r.RankName 
            FROM Players p
            LEFT JOIN Branches b ON p.BranchID = b.BranchID
            LEFT JOIN Ranks r ON p.RankID = r.RankID
            WHERE 1=1
        """
        
        params = []
        if branch_id:
            query += " AND p.BranchID = ?"
            params.append(branch_id)
        if rank_id:
            query += " AND p.RankID = ?"
            params.append(rank_id)
        
        cursor.execute(query, params)
        columns = [column[0] for column in cursor.description]
        results = []
        
        for row in cursor.fetchall():
            row_dict = dict(zip(columns, row))
            if 'JoinDate' in row_dict and row_dict['JoinDate']:
                row_dict['JoinDate'] = row_dict['JoinDate'].strftime('%Y-%m-%d')
            if 'Salary' in row_dict and row_dict['Salary']:
                row_dict['Salary'] = float(row_dict['Salary'])
            results.append(row_dict)
        
        conn.close()
        return jsonify(results)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/games', methods=['GET'])
def get_games():
    """Get all games with optional filters"""
    try:
        branch_id = request.args.get('branchId')
        season = request.args.get('season')
        
        conn = get_db_connection()
        if conn is None:
            return jsonify({'error': 'Database connection failed'}), 500
        cursor = conn.cursor()
        
        query = "SELECT * FROM Games WHERE 1=1"
        params = []
        
        if branch_id:
            query += " AND BranchID = ?"
            params.append(branch_id)
        if season:
            query += " AND Season = ?"
            params.append(season)
        
        cursor.execute(query, params)
        columns = [column[0] for column in cursor.description]
        results = []
        
        for row in cursor.fetchall():
            row_dict = dict(zip(columns, row))
            if 'GameDate' in row_dict and row_dict['GameDate']:
                row_dict['GameDate'] = row_dict['GameDate'].strftime('%Y-%m-%d')
            results.append(row_dict)
        
        conn.close()
        return jsonify(results)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/incomes', methods=['GET'])
def get_incomes():
    """Get all incomes with optional filters"""
    try:
        branch_id = request.args.get('branchId')
        
        conn = get_db_connection()
        if conn is None:
            return jsonify({'error': 'Database connection failed'}), 500
        cursor = conn.cursor()
        
        query = "SELECT * FROM Incomes WHERE 1=1"
        params = []
        
        if branch_id:
            query += " AND BranchID = ?"
            params.append(branch_id)
        
        cursor.execute(query, params)
        columns = [column[0] for column in cursor.description]
        results = []
        
        for row in cursor.fetchall():
            row_dict = dict(zip(columns, row))
            if 'IncomeDate' in row_dict and row_dict['IncomeDate']:
                row_dict['IncomeDate'] = row_dict['IncomeDate'].strftime('%Y-%m-%d')
            if 'Amount' in row_dict and row_dict['Amount']:
                row_dict['Amount'] = float(row_dict['Amount'])
            results.append(row_dict)
        
        conn.close()
        return jsonify(results)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/stats/summary', methods=['GET'])
def get_summary_stats():
    """Get aggregated statistics"""
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({'error': 'Database connection failed'}), 500
        cursor = conn.cursor()
        
        stats = {}
        
        # Total players
        cursor.execute("SELECT COUNT(*) as count FROM Players")
        stats['totalPlayers'] = cursor.fetchone()[0]
        
        # Total games
        cursor.execute("SELECT COUNT(*) as count FROM Games")
        stats['totalGames'] = cursor.fetchone()[0]
        
        # Total income
        cursor.execute("SELECT SUM(Amount) as total FROM Incomes")
        total_income = cursor.fetchone()[0]
        stats['totalIncome'] = float(total_income) if total_income else 0
        
        # Win rate
        cursor.execute("""
            SELECT 
                CAST(SUM(CASE WHEN Result = 'Win' THEN 1 ELSE 0 END) AS FLOAT) / 
                COUNT(*) * 100 as winRate
            FROM Games
        """)
        win_rate = cursor.fetchone()[0]
        stats['winRate'] = float(win_rate) if win_rate else 0
        
        conn.close()
        return jsonify(stats)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/analytics/income-by-branch', methods=['GET'])
def get_income_by_branch():
    """Get income aggregated by branch"""
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({'error': 'Database connection failed'}), 500
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                b.BranchName,
                SUM(i.Amount) as TotalIncome
            FROM Incomes i
            JOIN Branches b ON i.BranchID = b.BranchID
            GROUP BY b.BranchName
            ORDER BY TotalIncome DESC
        """)
        
        columns = [column[0] for column in cursor.description]
        results = []
        
        for row in cursor.fetchall():
            row_dict = dict(zip(columns, row))
            if 'TotalIncome' in row_dict and row_dict['TotalIncome']:
                row_dict['TotalIncome'] = float(row_dict['TotalIncome'])
            results.append(row_dict)
        
        conn.close()
        return jsonify(results)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/analytics/players-by-position', methods=['GET'])
def get_players_by_position():
    """Get player count by position"""
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({'error': 'Database connection failed'}), 500
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                Position,
                COUNT(*) as Count
            FROM Players
            GROUP BY Position
        """)
        
        columns = [column[0] for column in cursor.description]
        results = []
        
        for row in cursor.fetchall():
            results.append(dict(zip(columns, row)))
        
        conn.close()
        return jsonify(results)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/analytics/players-by-rank', methods=['GET'])
def get_players_by_rank():
    """Get player count by rank"""
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({'error': 'Database connection failed'}), 500
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                r.RankName,
                COUNT(p.PlayerID) as Count
            FROM Ranks r
            LEFT JOIN Players p ON r.RankID = p.RankID
            GROUP BY r.RankName, r.Level
            ORDER BY r.Level
        """)
        
        columns = [column[0] for column in cursor.description]
        results = []
        
        for row in cursor.fetchall():
            results.append(dict(zip(columns, row)))
        
        conn.close()
        return jsonify(results)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/analytics/top-players', methods=['GET'])
def get_top_players():
    """Get top players by salary"""
    try:
        limit = request.args.get('limit', 10)
        
        conn = get_db_connection()
        if conn is None:
            return jsonify({'error': 'Database connection failed'}), 500

        cursor = conn.cursor()
        
        cursor.execute(f"""
            SELECT TOP {limit}
                PlayerName,
                Position,
                Salary,
                Nationality
            FROM Players
            ORDER BY Salary DESC
        """)
        
        columns = [column[0] for column in cursor.description]
        results = []
        
        for row in cursor.fetchall():
            row_dict = dict(zip(columns, row))
            if 'Salary' in row_dict and row_dict['Salary']:
                row_dict['Salary'] = float(row_dict['Salary'])
            results.append(row_dict)
        
        conn.close()
        return jsonify(results)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/players/<int:player_id>', methods=['GET'])
def get_player(player_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT p.*, b.BranchName, r.RankName
            FROM Players p
            LEFT JOIN Branches b ON p.BranchID = b.BranchID
            LEFT JOIN Ranks r ON p.RankID = r.RankID
            WHERE p.PlayerID = ?
        """, player_id)

        row = cursor.fetchone()
        if not row:
            return jsonify({'error': 'Player not found'}), 404

        columns = [column[0] for column in cursor.description]
        result = dict(zip(columns, row))

        if result.get('JoinDate'):
            result['JoinDate'] = result['JoinDate'].strftime('%Y-%m-%d')
        if result.get('Salary'):
            result['Salary'] = float(result['Salary'])

        conn.close()
        return jsonify(result)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    print("=" * 60)
    print("🚀 Starting Premier League Dashboard API...")
    print("=" * 60)
    print("📊 Server running on: http://localhost:5000")
    print("🌐 Dashboard URL: http://localhost:5000")
    print("🔗 API Health Check: http://localhost:5000/api/health")
    print("=" * 60)
    app.run(debug=True, host='0.0.0.0', port=5000)