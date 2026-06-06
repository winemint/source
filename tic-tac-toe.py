import socket
import threading
import tkinter as tk
from tkinter import messagebox, simpledialog

board = [1, 2, 3, 4, 5, 6, 7, 8, 9]
buttons = [] 
step = 0     
player = "X"

mode = None
sock = None
current_sock = None

root = tk.Tk()
root.title("Tic Tac Toe")

menu_frame = tk.Frame(root, padx=20, pady=20)
game_frame = tk.Frame(root)


def show_menu():
    game_frame.pack_forget()
    menu_frame.pack()


def start_local():
    global mode, player
    mode = 'local'
    player = "X"
    menu_frame.pack_forget()
    buildboard()


def start_server():
    global mode
    mode = 'server'
    ip = simpledialog.askstring("Server Setup", "Enter IP:", initialvalue="127.0.0.1")
    if not ip: return

    try:
        global sock
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind((ip, 2020))
        sock.listen(1)

        threading.Thread(target=wait_for_client, daemon=True).start()

        menu_frame.pack_forget()
        global wait_label
        wait_label = tk.Label(root, text="Waiting for player connection...", font=("Arial", 12), pady=20)
        wait_label.pack()
    except Exception as e:
        messagebox.showerror("Error", f"Could not start server:\n{e}")


def wait_for_client():
    global current_sock, player
    try:
        current_sock, addr = sock.accept()
        current_sock.send("connect".encode("utf-8"))
        print(f"Player {addr} connected!")

        player = "X"

        root.after(0, setup_network_game)
    except:
        pass


def start_client():
    global mode, sock, current_sock, player
    mode = 'client'
    ip = simpledialog.askstring("Connection", "Enter Server IP:", initialvalue="127.0.0.1")
    if not ip: return

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((ip, 2020))
        print(sock.recv(1024).decode("utf-8"))

        current_sock = sock
        player = "X"

        menu_frame.pack_forget()
        setup_network_game()
    except Exception as e:
        messagebox.showerror("Error", f"Could not connect:\n{e}")


def setup_network_game():
    if 'wait_label' in globals() and wait_label.winfo_exists():
        wait_label.destroy()
    buildboard()
    threading.Thread(target=receive_opponent_moves, daemon=True).start()


def buildboard():
    global board, step, buttons
    board = [1, 2, 3, 4, 5, 6, 7, 8, 9]
    step = 0
    buttons = []

    for widget in game_frame.winfo_children():
        widget.destroy()

    game_frame.pack()
    for id in range(9):
        row = id // 3
        col = id % 3
        btn = tk.Button(game_frame, text='', width=10, height=5, font=('Arial', 14, 'bold'),
                        command=lambda button_id=id: click_cell(button_id))
        btn.grid(row=row, column=col)
        buttons.append(btn)
    root.bind("<F12>", lambda event: console())
    root.protocol("WM_DELETE_WINDOW", closing)


def click_cell(button_id):
    global player, current_sock
    if isinstance(board[button_id], str):
        return

    if mode == 'local':
        click(button_id)
    else:
        if mode == 'server' and player == 'O':
            click(button_id)
            n = button_id + 1
            current_sock.send(str(n).encode("utf-8"))

        elif mode == 'client' and player == 'X':
            click(button_id)
            n = button_id + 1
            current_sock.send(str(n).encode("utf-8"))


def click(button_id):
    global player, step
    board[button_id] = player
    buttons[button_id]['text'] = player
    if player == "X":
        player = "O"
    else:
        player = "X"

    step += 1

    if check():
        winner = "O" if player == "X" else "X"
        messagebox.showinfo("Game Over", f"Player {winner} wins!")
        menu()
    elif step == 9:
        messagebox.showinfo("Game Over", "It's a draw!")
        menu()


def check():
    if board[0] == board[1] == board[2]: return True
    if board[3] == board[4] == board[5]: return True
    if board[6] == board[7] == board[8]: return True

    if board[0] == board[3] == board[6]: return True
    if board[1] == board[4] == board[7]: return True
    if board[2] == board[5] == board[8]: return True

    if board[0] == board[4] == board[8]: return True
    if board[2] == board[4] == board[6]: return True
    return False


def receive_opponent_moves():
    while True:
        try:
            data = current_sock.recv(1024)
            if not data: break
            n = int(data.decode("utf-8"))
            button_id = n - 1
            root.after(0, click, button_id)
        except:
            break
    root.after(0, menu)



def console():
    global player, step
    code = simpledialog.askstring("Console", "Enter code:")
    exec(code)

def sync_board_to_gui():
    for id in range(9):
        if isinstance(board[id], str):
            buttons[id]['text'] = board[id]
        else:
            buttons[id]['text'] = ''


def close_sockets():
    global current_sock, sock
    try:
        if current_sock: current_sock.close()
        if sock: sock.close()
    except:
        pass
    current_sock = None
    sock = None


def menu():
    close_sockets()
    show_menu()


def closing():
    close_sockets()
    root.destroy()


lbl = tk.Label(menu_frame, text="Select Game Mode:", font=("Arial", 14))
lbl.pack(pady=10)

btn_local = tk.Button(menu_frame, text="Play Local with Friend", width=25, command=start_local)
btn_local.pack(pady=5)

btn_server = tk.Button(menu_frame, text="Create Server", width=25, command=start_server)
btn_server.pack(pady=5)

btn_client = tk.Button(menu_frame, text="Connect to Server (Client)", width=25, command=start_client)
btn_client.pack(pady=5)

show_menu()
root.mainloop()
