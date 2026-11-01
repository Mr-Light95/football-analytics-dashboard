# Football Analytics Dashboard

A coursework data visualization project for exploring football club data through an interactive web dashboard.

## Source features

- amCharts 5 visualizations for branch income, player positions, player ranks and top salaries.
- Branch and rank filters, player cards, summary statistics and income data.
- Python Flask API connected to a local SQL Server database using pyodbc.
- An alternative Node.js/Express API is included as an earlier implementation.

## Stack

HTML, CSS, JavaScript, amCharts 5, Python, Flask, SQL Server and pyodbc.

## Local setup

1. Install Python and Microsoft ODBC Driver 17 for SQL Server.
2. Install dependencies: `pip install -r requirements.txt`.
3. Restore the project's `PremierLeagueClub` database to SQL Server LocalDB, or update `DB_CONFIG` in `dv.py` for your local instance.
4. Run `python dv.py` and open `http://localhost:5000`.

## Current limitations

The supplied source archive does **not** contain a database backup, schema or sample data. API-backed charts require the original database; this repository alone does not reproduce the full data flow. The frontend loads amCharts from its CDN and needs internet access.

The optional `server.js` expects `config.js`, whereas the archive supplies `config.1.js`, and does not include a package manifest. The documented setup uses the Python backend. These are coursework source files, not a production deployment. No live database or end-to-end run has been verified for this packaged snapshot.
