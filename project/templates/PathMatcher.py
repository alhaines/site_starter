#!/usr/bin/env python3
"""
Standalone PathMatcher GUI (no web server).

Usage:
  python3 templates/PathMatcher.py

This opens a simple tkinter GUI that:
 - Loads titles from newmedia.drwho (id, title, episodes)
 - For each title you can search newmedia.dr_who_master.file_path with a LIKE %title% query
 - Results show as selectable checkboxes; selecting one fills the filepath input
 - Edit/compose episodes in the episodes box and press Add to update newmedia.drwho.episodes for that title
 - After adding, the app advances to the next title

Prerequisites: pymysql and a config.py containing DB_CONFIG dict for pymysql.connect

If DB_CONFIG is not found, the app will stop and print an instruction message.

"""

import sys
import os
import threading
try:
    import tkinter as tk
    from tkinter import ttk, messagebox
except Exception as e:
    print('tkinter is required to run this GUI. On Debian/Ubuntu install python3-tk')
    raise

try:
    import pymysql
except Exception:
    print('pymysql is required. Install with: pip3 install pymysql')
    raise

# load DB config
try:
    from config import DB_CONFIG
except Exception:
    DB_CONFIG = None


def get_db_connection():
    """Establishes and returns a database connection."""
    if DB_CONFIG is None:
        msg = ("DB_CONFIG not found in config.py.\n\nPlease create a config.py with DB_CONFIG dict for pymysql, e.g.:\n\n"
               "DB_CONFIG = {'host':'localhost','user':'user','password':'pass','db':'yourdb','charset':'utf8mb4','cursorclass':pymysql.cursors.DictCursor}\n")
        raise RuntimeError(msg)
    try:
        conn = pymysql.connect(**DB_CONFIG)
        return conn
    except pymysql.err.OperationalError as e:
        raise


class PathMatcherApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('PathMatcher')
        self.geometry('900x640')

        # data
        self.titles = []  # list of dicts: id,title,episodes
        self.index = -1
        self.search_results = []  # current search rows
        self.check_vars = []

        self.create_widgets()

    def create_widgets(self):
        frm = ttk.Frame(self, padding=10)
        frm.pack(fill='both', expand=True)

        # top controls
        top = ttk.Frame(frm)
        top.pack(fill='x')

        self.load_btn = ttk.Button(top, text='Load Titles', command=self.load_titles)
        self.load_btn.pack(side='left')

        self.prev_btn = ttk.Button(top, text='Prev', command=self.prev_title)
        self.prev_btn.pack(side='left', padx=(8,0))
        self.next_btn = ttk.Button(top, text='Next', command=self.next_title)
        self.next_btn.pack(side='left', padx=(8,0))

        # Title
        lbl = ttk.Label(frm, text='Title:')
        lbl.pack(anchor='w', pady=(8,0))
        self.title_var = tk.StringVar()
        self.title_entry = ttk.Entry(frm, textvariable=self.title_var, state='readonly')
        self.title_entry.pack(fill='x')

        # filepath + search
        row = ttk.Frame(frm)
        row.pack(fill='x', pady=(8,0))
        self.filepath_var = tk.StringVar()
        self.filepath_entry = ttk.Entry(row, textvariable=self.filepath_var)
        self.filepath_entry.pack(side='left', fill='x', expand=True)
        self.search_btn = ttk.Button(row, text='Search', command=self.do_search)
        self.search_btn.pack(side='left', padx=(8,0))

        # results list (scrollable)
        results_lbl = ttk.Label(frm, text='Search results (select to use as filepath)')
        results_lbl.pack(anchor='w', pady=(8,0))

        self.results_canvas = tk.Canvas(frm, height=220)
        self.results_frame = ttk.Frame(self.results_canvas)
        self.scrollbar = ttk.Scrollbar(frm, orient='vertical', command=self.results_canvas.yview)
        self.results_canvas.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.pack(side='right', fill='y')
        self.results_canvas.pack(fill='x')
        self.results_canvas.create_window((0,0), window=self.results_frame, anchor='nw')
        self.results_frame.bind('<Configure>', lambda e: self.results_canvas.configure(scrollregion=self.results_canvas.bbox('all')))

        # episodes box
        ep_lbl = ttk.Label(frm, text='Episodes (will be saved into newmedia.drwho.episodes)')
        ep_lbl.pack(anchor='w', pady=(8,0))
        self.episodes_text = tk.Text(frm, height=8)
        self.episodes_text.pack(fill='both', expand=True)

        # add button
        btn_row = ttk.Frame(frm)
        btn_row.pack(fill='x', pady=(8,0))
        self.add_btn = ttk.Button(btn_row, text='Add (save episodes & advance)', command=self.add_and_advance)
        self.add_btn.pack(side='left')
        self.status_lbl = ttk.Label(btn_row, text='Status: idle')
        self.status_lbl.pack(side='left', padx=(8,0))

    def set_status(self, text):
        self.status_lbl.config(text='Status: '+text)

    def load_titles(self):
        self.set_status('loading titles...')
        try:
            conn = get_db_connection()
            with conn.cursor(pymysql.cursors.DictCursor) as cur:
                cur.execute('SELECT id, title, episodes FROM newmedia.drwho ORDER BY id ASC')
                rows = cur.fetchall()
            conn.close()
        except Exception as e:
            messagebox.showerror('DB error', str(e))
            self.set_status('error loading titles')
            return
        self.titles = rows
        if not self.titles:
            messagebox.showinfo('Info', 'No titles found in newmedia.drwho')
            self.set_status('no titles')
            return
        self.index = 0
        self.show_current()
        self.set_status('titles loaded')

    def show_current(self):
        if self.index<0 or self.index>=len(self.titles):
            self.title_var.set('')
            self.episodes_text.delete('1.0', 'end')
            self.filepath_var.set('')
            self.set_status('out of range')
            return
        row = self.titles[self.index]
        self.title_var.set(row.get('title') or '')
        self.episodes_text.delete('1.0', 'end')
        self.episodes_text.insert('1.0', row.get('episodes') or '')
        self.filepath_var.set('')
        self.clear_results()
        self.set_status(f'showing {self.index+1}/{len(self.titles)}')

    def prev_title(self):
        if self.index>0:
            self.index -=1
            self.show_current()

    def next_title(self):
        if self.index < len(self.titles)-1:
            self.index +=1
            self.show_current()

    def clear_results(self):
        for child in self.results_frame.winfo_children():
            child.destroy()
        self.check_vars = []
        self.search_results = []

    def do_search(self):
        title = self.title_var.get()
        if not title:
            messagebox.showinfo('Info','No title to search')
            return
        self.set_status('searching...')
        threading.Thread(target=self._search_thread, args=(title,), daemon=True).start()

    def _search_thread(self, title):
        try:
            conn = get_db_connection()
            with conn.cursor(pymysql.cursors.DictCursor) as cur:
                pattern = f"%{title}%"
                cur.execute('SELECT id, file_path FROM newmedia.dr_who_master WHERE file_path LIKE %s LIMIT 200', (pattern,))
                rows = cur.fetchall()
            conn.close()
        except Exception as e:
            self.after(0, lambda: (messagebox.showerror('DB error', str(e)), self.set_status('search error')))
            return
        self.search_results = rows
        self.after(0, self.populate_results)

    def populate_results(self):
        self.clear_results()
        if not self.search_results:
            lbl = ttk.Label(self.results_frame, text='(no results)')
            lbl.pack(anchor='w')
            self.set_status('no results')
            return
        for i, r in enumerate(self.search_results):
            var = tk.IntVar(value=0)
            cb = ttk.Checkbutton(self.results_frame, variable=var, text=r.get('file_path'))
            # when selected, unselect others and set filepath
            def make_cmd(v=var, path=r.get('file_path')):
                def cmd():
                    if v.get():
                        # uncheck others
                        for vv in self.check_vars:
                            if vv is not v:
                                vv.set(0)
                        self.filepath_var.set(path)
                    else:
                        self.filepath_var.set('')
                return cmd
            cb.config(command=make_cmd())
            cb.pack(anchor='w', fill='x')
            self.check_vars.append(var)
        self.set_status(f'found {len(self.search_results)} results')

    def add_and_advance(self):
        if self.index<0 or self.index>=len(self.titles):
            return
        drwho_id = self.titles[self.index]['id']
        episodes_text = self.episodes_text.get('1.0', 'end').strip()
        try:
            conn = get_db_connection()
            with conn.cursor() as cur:
                cur.execute('UPDATE newmedia.drwho SET episodes=%s WHERE id=%s', (episodes_text, drwho_id))
                conn.commit()
            conn.close()
        except Exception as e:
            messagebox.showerror('DB error', str(e))
            self.set_status('save error')
            return
        self.set_status('saved')
        # advance index
        if self.index < len(self.titles)-1:
            self.index += 1
            self.show_current()
        else:
            messagebox.showinfo('Done', 'Processed all titles')
            self.set_status('done')


if __name__ == '__main__':
    app = PathMatcherApp()
    try:
        app.mainloop()
    except Exception as e:
        print('Error running app:', e)
