#!/usr/bin/env python3
"""
Pwnagotchi Analyzer - Interface web pour analyser les captures WiFi
ATTENTION: Usage éthique uniquement - Vos propres réseaux ou avec autorisation
"""

from flask import Flask, render_template, request, jsonify, send_file, flash, redirect, url_for
from werkzeug.utils import secure_filename
import os
import subprocess
import json
import time
from datetime import datetime
import threading
import uuid
import re

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this'

# Configuration
UPLOAD_FOLDER = '/app/captures'
RESULTS_FOLDER = '/app/results'
WORDLISTS_FOLDER = '/app/wordlists'
ALLOWED_EXTENSIONS = {'pcap', 'cap', 'hccapx', 'hc22000'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB max

# Stockage des tâches en cours
active_tasks = {}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_wordlists():
    """Récupère la liste des wordlists disponibles"""
    wordlists = []
    if not os.path.exists(WORDLISTS_FOLDER):
        return wordlists
    for file in os.listdir(WORDLISTS_FOLDER):
        if file.endswith('.txt'):
            size = os.path.getsize(os.path.join(WORDLISTS_FOLDER, file))
            wordlists.append({
                'name': file,
                'size': f"{size // 1024 // 1024}MB" if size > 1024*1024 else f"{size // 1024}KB"
            })
    return wordlists

def convert_pcap_to_hashcat(pcap_file):
    """Convertit un fichier PCAP au format hashcat"""
    try:
        base_name = os.path.splitext(pcap_file)[0]
        hash_file = f"{base_name}.hc22000"
        
        cmd = f"hcxpcapngtool -o {hash_file} {pcap_file}"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0 and os.path.exists(hash_file):
            return hash_file
        else:
            return None
    except Exception as e:
        print(f"Erreur conversion: {e}")
        return None

def run_hashcat_attack(hash_file, wordlist, task_id):
    """Lance une attaque hashcat avec progression réelle et messages explicites"""
    try:
        active_tasks[task_id]['status'] = 'running'
        active_tasks[task_id]['progress'] = 0
        wordlist_path = os.path.join(WORDLISTS_FOLDER, wordlist)
        output_file = os.path.join(RESULTS_FOLDER, f"{task_id}_result.txt")
        print(f"=== DÉBUT ATTACQUE {task_id} ===")
        print(f"Hash file: {hash_file}")
        print(f"Wordlist: {wordlist_path}")
        print(f"Output: {output_file}")
        if not os.path.exists(hash_file) or os.path.getsize(hash_file) == 0:
            active_tasks[task_id]['status'] = 'failed'
            active_tasks[task_id]['error'] = 'Fichier hash vide ou introuvable - Aucun handshake valide dans le PCAP.'
            print(f"ERREUR: Fichier hash vide ou introuvable")
            return
        cmd = f"hashcat -m 22000 -a 0 {hash_file} {wordlist_path} --outfile={output_file} --force --status --status-timer=10"
        print(f"Lancement de la commande: {cmd}")
        process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
        progress = 0
        start_time = time.time()
        progress_re = re.compile(r"Progress\\.\\.\\.\\.\\.\\.\\.\\.: (\\d+)/(\\d+) \\((\\d+\\.\\d+)%\\)")
        try:
            for line in process.stdout:
                print(f"[hashcat] {line.strip()}")
                match = progress_re.search(line)
                if match:
                    percent = float(match.group(3))
                    progress = int(percent)
                    active_tasks[task_id]['progress'] = progress
            process.wait()
        except Exception as e:
            print(f"Erreur lors de la lecture de la sortie hashcat: {e}")
        stdout, stderr = process.communicate()
        print(f"Hashcat terminé avec code: {process.returncode}")
        print(f"STDOUT: {stdout[:500]}...")
        # Gestion explicite des cas
        if process.returncode == 0:
            if os.path.exists(output_file) and os.path.getsize(output_file) > 0:
                with open(output_file, 'r') as f:
                    content = f.read().strip()
                    if content:
                        active_tasks[task_id]['status'] = 'completed'
                        active_tasks[task_id]['result'] = content
                        active_tasks[task_id]['progress'] = 100
                        print(f"SUCCÈS: Mot de passe trouvé!")
                        return
            # Si retour 0 mais pas de résultat
            active_tasks[task_id]['status'] = 'failed'
            active_tasks[task_id]['error'] = "Aucun mot de passe du dictionnaire n'a permis de casser le handshake. Essayez un autre dictionnaire ou une attaque par masque."
            print(f"ÉCHEC: Aucun mot de passe trouvé (retour 0)")
        elif process.returncode == 1:
            # Code 1 = aucun mot de passe trouvé
            active_tasks[task_id]['status'] = 'failed'
            active_tasks[task_id]['error'] = "Aucun mot de passe du dictionnaire n'a permis de casser le handshake. Essayez un autre dictionnaire ou une attaque par masque."
            print(f"ÉCHEC: Aucun mot de passe trouvé (retour 1)")
        elif process.returncode == 255:
            active_tasks[task_id]['status'] = 'failed'
            active_tasks[task_id]['error'] = "Erreur technique lors de l'exécution de hashcat (code 255). Vérifiez les permissions, la mémoire ou la configuration."
            print(f"ERREUR: Hashcat a échoué avec le code 255")
        else:
            active_tasks[task_id]['status'] = 'failed'
            active_tasks[task_id]['error'] = f"Erreur technique inattendue lors de l'exécution de hashcat (code {process.returncode}). Regardez les logs pour plus de détails."
            print(f"ERREUR: Hashcat a échoué avec le code {process.returncode}")
        print(f"=== FIN ATTACQUE {task_id} ===")
    except Exception as e:
        active_tasks[task_id]['status'] = 'failed'
        active_tasks[task_id]['error'] = f'Exception: {str(e)}'
        print(f"EXCEPTION dans run_hashcat_attack: {e}")

@app.route('/')
def index():
    """Page d'accueil"""
    return render_template('index.html', wordlists=get_wordlists(), current_year=datetime.now().year)

@app.route('/upload', methods=['POST'])
def upload_file():
    """Upload d'un fichier PCAP"""
    if 'file' not in request.files:
        flash('Aucun fichier sélectionné')
        return redirect(request.url)
    
    file = request.files['file']
    wordlist = request.form.get('wordlist')
    
    if file.filename == '':
        flash('Aucun fichier sélectionné')
        return redirect(request.url)
    
    if file and file.filename and allowed_file(file.filename) and wordlist:
        if not file.filename:
            flash('Nom de fichier invalide')
            return redirect(request.url)
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Générer un ID unique pour la tâche
        task_id = str(uuid.uuid4())
        
        # Conversion PCAP vers hashcat
        hash_file = convert_pcap_to_hashcat(filepath)
        if not hash_file:
            flash('Erreur lors de la conversion du fichier PCAP')
            return redirect(url_for('index'))
        
        # Initialiser la tâche
        active_tasks[task_id] = {
            'id': task_id,
            'filename': filename,
            'wordlist': wordlist,
            'status': 'initializing',
            'progress': 0,
            'started_at': datetime.now().isoformat(),
            'result': None,
            'error': None
        }
        
        # Lancer l'attaque en arrière-plan
        thread = threading.Thread(target=run_hashcat_attack, args=(hash_file, wordlist, task_id))
        thread.start()
        
        return redirect(url_for('task_status', task_id=task_id))
    
    flash('Fichier ou wordlist invalide')
    return redirect(url_for('index'))

@app.route('/task/<task_id>')
def task_status(task_id):
    """Page de statut d'une tâche"""
    task = active_tasks.get(task_id)
    if not task:
        flash('Tâche non trouvée')
        return redirect(url_for('index'))
    
    return render_template('task_status.html', task=task, current_year=datetime.now().year)

@app.route('/api/task/<task_id>/status')
def api_task_status(task_id):
    """API pour récupérer le statut d'une tâche"""
    task = active_tasks.get(task_id)
    if not task:
        return jsonify({'error': 'Tâche non trouvée'}), 404
    
    return jsonify(task)

@app.route('/tasks')
def list_tasks():
    """Liste de toutes les tâches"""
    return render_template('tasks.html', tasks=list(active_tasks.values()), current_year=datetime.now().year)

if __name__ == '__main__':
    # Créer les dossiers nécessaires
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(RESULTS_FOLDER, exist_ok=True)
    os.makedirs(os.path.join(os.path.dirname(__file__), 'static'), exist_ok=True)
    
    print("🚀 Pwnagotchi Analyzer démarré!")
    print("⚠️  RAPPEL: Usage éthique uniquement - Vos propres réseaux!")
    print("🌐 Interface disponible sur: http://localhost:8888")
    
    app.run(host='0.0.0.0', port=8888, debug=True)