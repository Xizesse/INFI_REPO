import opcua

def connect_to_server(gui):
    try:
        # OPC UA connect logic here
        client.connect()
        gui.status_label.config(text="Connected", fg="green")
    except Exception as e:
        messagebox.showerror("Connection Error", str(e))

def disconnect_server(gui):
    try:
        # OPC UA disconnect logic here
        client.disconnect()
        gui.status_label.config(text="Disconnected", fg="red")
    except Exception as e:
        messagebox.showerror("Disconnection Error", str(e))

if __name__ == "__main__":
    url = "opc.tcp://172.27.64.1:4840"
    client = opcua.Client(url)

    root = tk.Tk()
    app = OPCUAClientGUI(root, lambda: connect_to_server(app), lambda: disconnect_server(app))
    root.mainloop()