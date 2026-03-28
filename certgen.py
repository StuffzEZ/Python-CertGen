import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import subprocess

# ----------------------------
# Tooltip Helper
# ----------------------------
class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        widget.bind("<Enter>", self.show)
        widget.bind("<Leave>", self.hide)
        self.tip = None

    def show(self, _):
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + 20
        self.tip = tk.Toplevel(self.widget)
        self.tip.wm_overrideredirect(True)
        self.tip.geometry(f"+{x}+{y}")
        label = tk.Label(self.tip, text=self.text, bg="black", fg="white",
                         padx=6, pady=4, relief="solid", borderwidth=1)
        label.pack()

    def hide(self, _):
        if self.tip:
            self.tip.destroy()
            self.tip = None


# ----------------------------
# Certificate Generator
# ----------------------------
def generate_cert():
    subject = subject_var.get()
    key_algo = algo_var.get()
    key_length = key_length_var.get()
    hash_algo = hash_var.get()
    cert_type = type_var.get()
    store = store_var.get()
    years = validity_var.get()

    try:
        ps_command = f"""
        $cert = New-SelfSignedCertificate `
            -Subject "{subject}" `
            -Type {cert_type} `
            -KeyAlgorithm {key_algo} `
            -KeyLength {key_length} `
            -HashAlgorithm {hash_algo} `
            -CertStoreLocation "{store}" `
            -NotAfter (Get-Date).AddYears({years});

        $cert.Thumbprint
        """

        result = subprocess.check_output(
            ["powershell", "-Command", ps_command],
            text=True
        )

        output_box.delete("1.0", tk.END)
        output_box.insert(tk.END, f"Certificate Created!\nThumbprint:\n{result}")

    except Exception as e:
        messagebox.showerror("Error", str(e))


# ----------------------------
# File Signing Function
# ----------------------------
def sign_file():
    file_path = filedialog.askopenfilename()
    if not file_path:
        return

    try:
        ps_command = f"""
        $cert = Get-ChildItem Cert:\\CurrentUser\\My | Select-Object -First 1
        Set-AuthenticodeSignature "{file_path}" -Certificate $cert
        """

        subprocess.run(["powershell", "-Command", ps_command], check=True)

        messagebox.showinfo("Success", "File signed successfully!")

    except Exception as e:
        messagebox.showerror("Error", str(e))


# ----------------------------
# GUI Setup
# ----------------------------
root = tk.Tk()
root.title("Self-Signed Certificate Tool")
root.geometry("500x450")

# Subject
tk.Label(root, text="Subject (CN=...):").pack()
subject_var = tk.StringVar(value="CN=MyCert")
tk.Entry(root, textvariable=subject_var, width=40).pack()

# Type
tk.Label(root, text="Certificate Type:").pack()
type_var = tk.StringVar(value="CodeSigningCert")
type_menu = ttk.Combobox(root, textvariable=type_var, values=[
    "CodeSigningCert",
    "SSLServerAuthentication",
    "DocumentEncryption"
])
type_menu.pack()

ToolTip(type_menu, "Choose what the certificate is used for")

# Key Algorithm
tk.Label(root, text="Key Algorithm:").pack()
algo_var = tk.StringVar(value="RSA")
algo_menu = ttk.Combobox(root, textvariable=algo_var, values=["RSA", "ECDSA"])
algo_menu.pack()

ToolTip(algo_menu, "RSA = more compatible\nECDSA = faster, modern")

# Key Length
tk.Label(root, text="Key Length:").pack()
key_length_var = tk.StringVar(value="2048")
tk.Entry(root, textvariable=key_length_var).pack()

# Hash
tk.Label(root, text="Hash Algorithm:").pack()
hash_var = tk.StringVar(value="SHA256")
hash_menu = ttk.Combobox(root, textvariable=hash_var, values=[
    "SHA256", "SHA384", "SHA512"
])
hash_menu.pack()

ToolTip(hash_menu, "SHA256 is standard and recommended")

# Validity
tk.Label(root, text="Validity (Years):").pack()
validity_var = tk.StringVar(value="1")
tk.Entry(root, textvariable=validity_var).pack()

# Store
tk.Label(root, text="Store Location:").pack()
store_var = tk.StringVar(value="Cert:\\CurrentUser\\My")
store_menu = ttk.Combobox(root, textvariable=store_var, values=[
    "Cert:\\CurrentUser\\My",
    "Cert:\\LocalMachine\\My"
])
store_menu.pack()

ToolTip(store_menu, "CurrentUser = you only\nLocalMachine = all users (admin required)")

# Buttons
tk.Button(root, text="Generate Certificate", command=generate_cert).pack(pady=10)
tk.Button(root, text="Sign File (.bat/.exe)", command=sign_file).pack(pady=5)

# Output box
output_box = tk.Text(root, height=6)
output_box.pack(fill="both", expand=True, padx=10, pady=10)

root.mainloop()
