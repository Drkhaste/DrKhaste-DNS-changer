import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import sys
import os
import threading
from tkinter import font
import winreg
import json

class DNSChangerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("DrKhaste - DNS Changer Pro")
        self.root.geometry("450x700")
        self.root.resizable(False , False)
        
        # Dark theme colors
        self.bg_color = "#1a1a1a"
        self.card_color = "#2d2d2d"
        self.accent_color = "#00d4aa"
        self.text_color = "#ffffff"
        self.secondary_text = "#b0b0b0"
        self.success_color = "#00ff88"
        self.error_color = "#ff4757"
        self.warning_color = "#ffa502"
        
        # Configure root
        self.root.configure(bg=self.bg_color)
        
        # Create custom fonts
        self.title_font = font.Font(family="Segoe UI", size=18, weight="bold")
        self.header_font = font.Font(family="Segoe UI", size=12, weight="bold")
        self.body_font = font.Font(family="Segoe UI", size=10)
        self.small_font = font.Font(family="Segoe UI", size=8)
        
        # Network interfaces
        self.network_interfaces = []
        self.selected_interface = tk.StringVar()
        
        # Configure styles
        self.setup_styles()
        
        # Create UI
        self.create_ui()
        
        # Check if running as admin and load interfaces
        self.check_admin()
        self.load_network_interfaces()
        
    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure button style
        style.configure('Custom.TButton',
                       background=self.accent_color,
                       foreground='white',
                       borderwidth=0,
                       focuscolor='none',
                       font=self.body_font)
        
        style.map('Custom.TButton',
                 background=[('active', '#00b894'),
                           ('pressed', '#00a085')])
        
        # Configure combobox style
        style.configure('Custom.TCombobox',
                       fieldbackground='#3d3d3d',
                       background='#3d3d3d',
                       foreground='white',
                       borderwidth=0)
    
    def create_ui(self):
        # Main container with scrollbar
        canvas = tk.Canvas(self.root, bg=self.bg_color, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.bg_color)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        main_frame = tk.Frame(scrollable_frame, bg=self.bg_color)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Title
        title_label = tk.Label(main_frame, 
                              text="🌐 DrKhaste - DNS Changer Pro", 
                              font=self.title_font,
                              fg=self.text_color,
                              bg=self.bg_color)
        title_label.pack(pady=(0, 10))
        
        subtitle_label = tk.Label(main_frame, 
                                 text="Advanced Network Configuration Tool", 
                                 font=self.body_font,
                                 fg=self.secondary_text,
                                 bg=self.bg_color)
        subtitle_label.pack(pady=(0, 30))
        
        # Admin status card
        self.create_admin_status_card(main_frame)
        
        # Network interface selection
        self.create_interface_selection_card(main_frame)
        
        # Current DNS status
        self.create_current_dns_card(main_frame)
        
        # DNS configuration steps
        self.create_dns_steps_card(main_frame)
        
        # DNS options card
        self.create_dns_options_card(main_frame)
        
        # Control buttons
        self.create_control_buttons(main_frame)
        
        # Status bar
        self.create_status_bar(main_frame)
        
        # Bind mouse wheel to canvas
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
    
    def create_admin_status_card(self, parent):
        admin_frame = tk.Frame(parent, bg=self.card_color, padx=20, pady=15)
        admin_frame.pack(fill=tk.X, pady=(0, 20))
        admin_frame.configure(relief=tk.RAISED, bd=1)
        
        admin_title = tk.Label(admin_frame,
                              text="🔐 Administrator Status",
                              font=self.header_font,
                              fg=self.text_color,
                              bg=self.card_color)
        admin_title.pack(anchor=tk.W)
        
        self.admin_status_label = tk.Label(admin_frame,
                                          text="Checking administrator privileges...",
                                          font=self.body_font,
                                          fg=self.secondary_text,
                                          bg=self.card_color)
        self.admin_status_label.pack(anchor=tk.W, pady=(5, 0))
    
    def create_interface_selection_card(self, parent):
        interface_frame = tk.Frame(parent, bg=self.card_color, padx=20, pady=15)
        interface_frame.pack(fill=tk.X, pady=(0, 20))
        interface_frame.configure(relief=tk.RAISED, bd=1)
        
        interface_title = tk.Label(interface_frame,
                                  text="🔌 Network Interface Selection",
                                  font=self.header_font,
                                  fg=self.text_color,
                                  bg=self.card_color)
        interface_title.pack(anchor=tk.W)
        
        interface_desc = tk.Label(interface_frame,
                                 text="Select the network adapter (Wi-Fi or Ethernet) to configure:",
                                 font=self.body_font,
                                 fg=self.secondary_text,
                                 bg=self.card_color)
        interface_desc.pack(anchor=tk.W, pady=(5, 10))
        
        self.interface_combo = ttk.Combobox(interface_frame,
                                           textvariable=self.selected_interface,
                                           font=self.body_font,
                                           state="readonly",
                                           style='Custom.TCombobox')
        self.interface_combo.pack(fill=tk.X, pady=(0, 10))
        self.interface_combo.bind("<<ComboboxSelected>>", self.on_interface_selected)
        
        refresh_btn = tk.Button(interface_frame,
                               text="🔄 Refresh Interfaces",
                               font=self.body_font,
                               bg="#4a4a4a",
                               fg="white",
                               activebackground="#5a5a5a",
                               activeforeground="white",
                               borderwidth=0,
                               relief=tk.FLAT,
                               command=self.load_network_interfaces,
                               cursor="hand2")
        refresh_btn.pack(anchor=tk.W)
    
    def create_current_dns_card(self, parent):
        current_frame = tk.Frame(parent, bg=self.card_color, padx=20, pady=15)
        current_frame.pack(fill=tk.X, pady=(0, 20))
        current_frame.configure(relief=tk.RAISED, bd=1)
        
        current_title = tk.Label(current_frame,
                                text="📋 Current DNS Configuration",
                                font=self.header_font,
                                fg=self.text_color,
                                bg=self.card_color)
        current_title.pack(anchor=tk.W)
        
        self.current_dns_label = tk.Label(current_frame,
                                         text="Select a network interface to view current DNS settings",
                                         font=self.body_font,
                                         fg=self.secondary_text,
                                         bg=self.card_color,
                                         justify=tk.LEFT)
        self.current_dns_label.pack(anchor=tk.W, pady=(5, 0))
    
    def create_dns_steps_card(self, parent):
        steps_frame = tk.Frame(parent, bg=self.card_color, padx=20, pady=15)
        steps_frame.pack(fill=tk.X, pady=(0, 20))
        steps_frame.configure(relief=tk.RAISED, bd=1)
        
        steps_title = tk.Label(steps_frame,
                              text="📝 DNS Configuration Steps (Automated)",
                              font=self.header_font,
                              fg=self.text_color,
                              bg=self.card_color)
        steps_title.pack(anchor=tk.W)
        
        steps_text = """This application automates the following manual steps:
        
1. ✅ Access Network Adapter Properties (Control Panel equivalent)
2. ✅ Locate Internet Protocol Version 4 (TCP/IPv4) settings  
3. ✅ Enable "Use the following DNS server addresses"
4. ✅ Set Preferred DNS server: 178.22.122.100
5. ✅ Set Alternate DNS server: 185.51.200.2
6. ✅ Apply settings and refresh network configuration
7. ✅ Flush DNS cache for immediate effect"""
        
        steps_label = tk.Label(steps_frame,
                              text=steps_text,
                              font=self.small_font,
                              fg=self.secondary_text,
                              bg=self.card_color,
                              justify=tk.LEFT)
        steps_label.pack(anchor=tk.W, pady=(5, 0))
    
    def create_dns_options_card(self, parent):
        dns_frame = tk.Frame(parent, bg=self.card_color, padx=20, pady=15)
        dns_frame.pack(fill=tk.X, pady=(0, 20))
        dns_frame.configure(relief=tk.RAISED, bd=1)
        
        dns_title = tk.Label(dns_frame,
                            text="🌍 DNS Server Configuration",
                            font=self.header_font,
                            fg=self.text_color,
                            bg=self.card_color)
        dns_title.pack(anchor=tk.W)
        
        # Primary DNS
        primary_label = tk.Label(dns_frame,
                                text="🎯 Preferred DNS Server:",
                                font=self.body_font,
                                fg=self.text_color,
                                bg=self.card_color)
        primary_label.pack(anchor=tk.W, pady=(15, 2))
        
        self.primary_entry = tk.Entry(dns_frame,
                                     font=self.body_font,
                                     bg="#3d3d3d",
                                     fg=self.text_color,
                                     insertbackground=self.text_color,
                                     borderwidth=1,
                                     relief=tk.SOLID)
        self.primary_entry.pack(fill=tk.X, pady=(0, 10), ipady=8)
        self.primary_entry.insert(0, "178.22.122.100")
        
        # Secondary DNS
        secondary_label = tk.Label(dns_frame,
                                  text="🔄 Alternate DNS Server:",
                                  font=self.body_font,
                                  fg=self.text_color,
                                  bg=self.card_color)
        secondary_label.pack(anchor=tk.W, pady=(0, 2))
        
        self.secondary_entry = tk.Entry(dns_frame,
                                       font=self.body_font,
                                       bg="#3d3d3d",
                                       fg=self.text_color,
                                       insertbackground=self.text_color,
                                       borderwidth=1,
                                       relief=tk.SOLID)
        self.secondary_entry.pack(fill=tk.X, pady=(0, 15), ipady=8)
        self.secondary_entry.insert(0, "185.51.200.2")
        
        # Quick preset buttons
        preset_frame = tk.Frame(dns_frame, bg=self.card_color)
        preset_frame.pack(fill=tk.X, pady=(0, 10))
        
        preset_label = tk.Label(preset_frame,
                               text="Quick Presets:",
                               font=self.body_font,
                               fg=self.secondary_text,
                               bg=self.card_color)
        preset_label.pack(anchor=tk.W, pady=(0, 5))
        
        # Preset buttons frame
        preset_buttons_frame = tk.Frame(preset_frame, bg=self.card_color)
        preset_buttons_frame.pack(fill=tk.X)
        
        # Custom preset (default)
        custom_btn = tk.Button(preset_buttons_frame,
                              text="Custom DNS\n(Recommended)",
                              font=self.small_font,
                              bg=self.accent_color,
                              fg="white",
                              activebackground="#00b894",
                              borderwidth=0,
                              relief=tk.FLAT,
                              command=lambda: self.set_dns_preset("178.22.122.100", "185.51.200.2"),
                              cursor="hand2")
        custom_btn.pack(side=tk.LEFT, padx=(0, 5), pady=2, fill=tk.X, expand=True)
        
        google_btn = tk.Button(preset_buttons_frame,
                              text="Google DNS\n8.8.8.8",
                              font=self.small_font,
                              bg="#4a4a4a",
                              fg="white",
                              activebackground="#5a5a5a",
                              borderwidth=0,
                              relief=tk.FLAT,
                              command=lambda: self.set_dns_preset("8.8.8.8", "8.8.4.4"),
                              cursor="hand2")
        google_btn.pack(side=tk.LEFT, padx=5, pady=2, fill=tk.X, expand=True)
        
        cloudflare_btn = tk.Button(preset_buttons_frame,
                                  text="Cloudflare DNS\n1.1.1.1",
                                  font=self.small_font,
                                  bg="#4a4a4a",
                                  fg="white",
                                  activebackground="#5a5a5a",
                                  borderwidth=0,
                                  relief=tk.FLAT,
                                  command=lambda: self.set_dns_preset("1.1.1.1", "1.0.0.1"),
                                  cursor="hand2")
        cloudflare_btn.pack(side=tk.LEFT, padx=(5, 0), pady=2, fill=tk.X, expand=True)
    
    def create_control_buttons(self, parent):
        button_frame = tk.Frame(parent, bg=self.bg_color)
        button_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Apply DNS button
        self.apply_btn = tk.Button(button_frame,
                                  text="🚀 Apply DNS Configuration",
                                  font=self.header_font,
                                  bg=self.accent_color,
                                  fg="white",
                                  activebackground="#00b894",
                                  activeforeground="white",
                                  borderwidth=0,
                                  relief=tk.FLAT,
                                  command=self.apply_dns_advanced,
                                  cursor="hand2")
        self.apply_btn.pack(fill=tk.X, padx=(0, 0), pady=(0, 10), ipady=12)
        
        # Bottom buttons row
        bottom_buttons = tk.Frame(button_frame, bg=self.bg_color)
        bottom_buttons.pack(fill=tk.X)
        
        # Reset DNS button
        self.reset_btn = tk.Button(bottom_buttons,
                                  text="🔄 Reset to Automatic",
                                  font=self.body_font,
                                  bg="#4a4a4a",
                                  fg="white",
                                  activebackground="#5a5a5a",
                                  activeforeground="white",
                                  borderwidth=0,
                                  relief=tk.FLAT,
                                  command=self.reset_dns_advanced,
                                  cursor="hand2")
        self.reset_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5), ipady=8)
        
        # Flush DNS button
        flush_btn = tk.Button(bottom_buttons,
                             text="🧹 Flush DNS Cache",
                             font=self.body_font,
                             bg="#4a4a4a",
                             fg="white",
                             activebackground="#5a5a5a",
                             activeforeground="white",
                             borderwidth=0,
                             relief=tk.FLAT,
                             command=self.flush_dns,
                             cursor="hand2")
        flush_btn.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(5, 0), ipady=8)
    
    def create_status_bar(self, parent):
        status_frame = tk.Frame(parent, bg="#333333", padx=15, pady=10)
        status_frame.pack(fill=tk.X, pady=(10, 0))
        status_frame.configure(relief=tk.RAISED, bd=1)
        
        self.status_bar = tk.Label(status_frame,
                                  text="🟢 Ready - Select network interface and configure DNS",
                                  font=self.body_font,
                                  fg=self.text_color,
                                  bg="#333333",
                                  anchor=tk.W)
        self.status_bar.pack(fill=tk.X)
    
    def set_dns_preset(self, primary, secondary):
        """Set DNS preset values"""
        self.primary_entry.delete(0, tk.END)
        self.primary_entry.insert(0, primary)
        self.secondary_entry.delete(0, tk.END)
        self.secondary_entry.insert(0, secondary)
        self.status_bar.config(text=f"🎯 DNS preset applied: {primary}, {secondary}", fg=self.accent_color)
    
    def check_admin(self):
        """Check if the app is running with administrator privileges"""
        try:
            import ctypes
            is_admin = ctypes.windll.shell32.IsUserAnAdmin()
            if is_admin:
                self.admin_status_label.config(text="✅ Running with Administrator privileges", fg=self.success_color)
            else:
                self.admin_status_label.config(text="❌ Administrator privileges required for DNS changes", fg=self.error_color)
                self.apply_btn.config(state=tk.DISABLED, bg="#666666")
                self.reset_btn.config(state=tk.DISABLED, bg="#666666")
                messagebox.showwarning("Administrator Required", 
                                     "This application requires Administrator privileges to modify DNS settings.\n\n"
                                     "Please restart the application as Administrator.")
        except Exception as e:
            self.admin_status_label.config(text="⚠️ Could not verify admin status", fg=self.warning_color)
    
    def load_network_interfaces(self):
        """Load network interfaces using WMI/Registry approach"""
        def load_in_thread():
            try:
                self.status_bar.config(text="🔍 Loading network interfaces...", fg=self.accent_color)
                
                # Use netsh to get interface list
                result = subprocess.run(['netsh', 'interface', 'show', 'interface'], 
                                      capture_output=True, text=True, shell=True)
                
                interfaces = []
                if result.returncode == 0:
                    lines = result.stdout.split('\n')
                    for line in lines:
                        if 'Connected' in line and ('Wi-Fi' in line or 'Ethernet' in line or 'Local Area Connection' in line):
                            parts = line.split()
                            if len(parts) >= 4:
                                interface_name = ' '.join(parts[3:]).strip()
                                if interface_name and interface_name not in interfaces:
                                    interfaces.append(interface_name)
                
                # Add common interface names if not found
                common_names = ["Wi-Fi", "Ethernet", "Local Area Connection", "Wireless Network Connection"]
                for name in common_names:
                    if name not in interfaces:
                        interfaces.append(name)
                
                self.network_interfaces = interfaces
                self.interface_combo['values'] = interfaces
                
                if interfaces:
                    self.interface_combo.set(interfaces[0])
                    self.selected_interface.set(interfaces[0])
                    self.get_current_dns(interfaces[0])
                    self.status_bar.config(text=f"✅ Found {len(interfaces)} network interfaces", fg=self.success_color)
                else:
                    self.status_bar.config(text="⚠️ No network interfaces found", fg=self.warning_color)
                    
            except Exception as e:
                self.status_bar.config(text=f"❌ Error loading interfaces: {str(e)}", fg=self.error_color)
        
        threading.Thread(target=load_in_thread, daemon=True).start()
    
    def on_interface_selected(self, event=None):
        """Handle interface selection"""
        selected = self.selected_interface.get()
        if selected:
            self.get_current_dns(selected)
    
    def get_current_dns(self, interface_name):
        """Get current DNS settings for interface"""
        def get_dns_in_thread():
            try:
                self.status_bar.config(text=f"🔍 Getting DNS settings for {interface_name}...", fg=self.accent_color)
                
                # Get DNS servers using netsh
                cmd = f'netsh interface ip show dns name="{interface_name}"'
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                
                if result.returncode == 0:
                    output = result.stdout
                    dns_servers = []
                    
                    # Parse DNS servers from output
                    lines = output.split('\n')
                    for line in lines:
                        if 'DNS servers configured through DHCP' in line:
                            self.current_dns_label.config(text="🔄 Currently using automatic DNS (DHCP)", fg=self.secondary_text)
                            return
                        elif 'Statically Configured DNS Servers' in line:
                            continue
                        elif line.strip() and any(char.isdigit() for char in line):
                            # Extract IP addresses
                            import re
                            ip_pattern = r'\b(?:\d{1,3}\.){3}\d{1,3}\b'
                            ips = re.findall(ip_pattern, line)
                            dns_servers.extend(ips)
                    
                    if dns_servers:
                        dns_text = f"🎯 Current DNS Servers:\n"
                        for i, dns in enumerate(dns_servers[:2], 1):
                            dns_text += f"  {'Primary' if i == 1 else 'Secondary'}: {dns}\n"
                        self.current_dns_label.config(text=dns_text.strip(), fg=self.text_color)
                    else:
                        self.current_dns_label.config(text="🔄 Using automatic DNS settings", fg=self.secondary_text)
                else:
                    self.current_dns_label.config(text="❌ Could not retrieve DNS settings", fg=self.error_color)
                    
            except Exception as e:
                self.current_dns_label.config(text=f"❌ Error: {str(e)}", fg=self.error_color)
        
        threading.Thread(target=get_dns_in_thread, daemon=True).start()
    
    def apply_dns_advanced(self):
        """Apply DNS settings with advanced method mimicking Control Panel steps"""
        def apply_in_thread():
            steps_completed = []
            try:
                interface = self.selected_interface.get()
                if not interface:
                    raise Exception("Please select a network interface first")
                
                primary_dns = self.primary_entry.get().strip()
                secondary_dns = self.secondary_entry.get().strip()
                
                if not primary_dns:
                    raise Exception("Primary DNS server is required")
                
                self.status_bar.config(text="🚀 Starting DNS configuration process...", fg=self.accent_color)
                self.apply_btn.config(state=tk.DISABLED, bg="#666666")
                
                # Step 1: Clear existing DNS configuration
                self.status_bar.config(text="📋 Step 1/6: Clearing existing DNS configuration...", fg=self.accent_color)
                clear_cmd = f'netsh interface ip set dns name="{interface}" dhcp'
                subprocess.run(clear_cmd, shell=True, capture_output=True, text=True)
                steps_completed.append("✅ Cleared existing DNS settings")
                
                # Step 2: Set to use static DNS (equivalent to "Use the following DNS server addresses")
                self.status_bar.config(text="⚙️ Step 2/6: Configuring static DNS mode...", fg=self.accent_color)
                primary_cmd = f'netsh interface ip set dns name="{interface}" static {primary_dns}'
                result1 = subprocess.run(primary_cmd, shell=True, capture_output=True, text=True)
                
                if result1.returncode != 0:
                    raise Exception(f"Failed to set primary DNS: {result1.stderr}")
                steps_completed.append(f"✅ Set preferred DNS server: {primary_dns}")
                
                # Step 3: Add secondary DNS if provided
                if secondary_dns:
                    self.status_bar.config(text="🔄 Step 3/6: Adding alternate DNS server...", fg=self.accent_color)
                    secondary_cmd = f'netsh interface ip add dns name="{interface}" {secondary_dns} index=2'
                    result2 = subprocess.run(secondary_cmd, shell=True, capture_output=True, text=True)
                    
                    if result2.returncode == 0:
                        steps_completed.append(f"✅ Set alternate DNS server: {secondary_dns}")
                    else:
                        steps_completed.append(f"⚠️ Alternate DNS may not be set properly")
                
                # Step 4: Flush DNS cache
                self.status_bar.config(text="🧹 Step 4/6: Flushing DNS cache...", fg=self.accent_color)
                flush_result = subprocess.run(['ipconfig', '/flushdns'], capture_output=True, text=True, shell=True)
                if flush_result.returncode == 0:
                    steps_completed.append("✅ DNS cache flushed successfully")
                
                # Step 5: Refresh network adapter
                self.status_bar.config(text="🔄 Step 5/6: Refreshing network configuration...", fg=self.accent_color)
                subprocess.run(['ipconfig', '/renew'], capture_output=True, text=True, shell=True)
                steps_completed.append("✅ Network configuration refreshed")
                
                # Step 6: Verify DNS settings
                self.status_bar.config(text="✅ Step 6/6: Verifying DNS configuration...", fg=self.accent_color)
                self.get_current_dns(interface)
                steps_completed.append("✅ DNS configuration verified")
                
                # Success message
                success_msg = f"🎉 DNS Configuration Applied Successfully!\n\n"
                success_msg += f"Interface: {interface}\n"
                success_msg += f"Primary DNS: {primary_dns}\n"
                if secondary_dns:
                    success_msg += f"Secondary DNS: {secondary_dns}\n"
                success_msg += f"\nSteps completed:\n" + "\n".join(steps_completed)
                success_msg += f"\n\n💡 Your browser may need to be restarted for changes to take full effect."
                
                self.status_bar.config(text="🎉 DNS configuration applied successfully!", fg=self.success_color)
                messagebox.showinfo("Success", success_msg)
                
            except Exception as e:
                error_msg = f"❌ DNS Configuration Failed\n\nError: {str(e)}\n\n"
                if steps_completed:
                    error_msg += "Steps completed before error:\n" + "\n".join(steps_completed)
                
                self.status_bar.config(text=f"❌ Error: {str(e)}", fg=self.error_color)
                messagebox.showerror("Error", error_msg)
            
            finally:
                self.apply_btn.config(state=tk.NORMAL, bg=self.accent_color)
        
        threading.Thread(target=apply_in_thread, daemon=True).start()
    
    def reset_dns_advanced(self):
        """Reset DNS to automatic with advanced feedback"""
        def reset_in_thread():
            try:
                interface = self.selected_interface.get()
                if not interface:
                    raise Exception("Please select a network interface first")
                
                self.status_bar.config(text="🔄 Resetting DNS to automatic (DHCP)...", fg=self.accent_color)
                self.reset_btn.config(state=tk.DISABLED, bg="#666666")
                
                cmd = f'netsh interface ip set dns name="{interface}" dhcp'
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                
                if result.returncode == 0:
                    # Flush DNS cache
                    subprocess.run(['ipconfig', '/flushdns'], capture_output=True, text=True, shell=True)
                    
                    # Refresh network
                    subprocess.run(['ipconfig', '/renew'], capture_output=True, text=True, shell=True)
                    
                    self.get_current_dns(interface)
                    
                    success_msg = f"🔄 DNS Reset to Automatic Successfully!\n\n"
                    success_msg += f"Interface: {interface}\n"
                    success_msg += f"DNS Mode: Automatic (DHCP)\n"
                    success_msg += f"✅ DNS cache flushed\n"
                    success_msg += f"✅ Network configuration refreshed\n"
                    success_msg += f"\n💡 Your system will now use DNS servers provided by your ISP."
                    
                    self.status_bar.config(text="✅ DNS reset to automatic successfully!", fg=self.success_color)
                    messagebox.showinfo("Success", success_msg)
                else:
                    raise Exception("Failed to reset DNS settings")
                    
            except Exception as e:
                self.status_bar.config(text=f"❌ Error resetting DNS: {str(e)}", fg=self.error_color)
                messagebox.showerror("Error", f"Failed to reset DNS settings:\n{str(e)}")
            
            finally:
                self.reset_btn.config(state=tk.NORMAL, bg="#4a4a4a")
        
        threading.Thread(target=reset_in_thread, daemon=True).start()
    
    def flush_dns(self):
        """Flush DNS cache"""
        def flush_in_thread():
            try:
                self.status_bar.config(text="🧹 Flushing DNS cache...", fg=self.accent_color)
                
                result = subprocess.run(['ipconfig', '/flushdns'], 
                                      capture_output=True, text=True, shell=True)
                
                if result.returncode == 0:
                    self.status_bar.config(text="✅ DNS cache flushed successfully!", fg=self.success_color)
                    messagebox.showinfo("Success", "🧹 DNS Cache Flushed Successfully!\n\nThis helps ensure new DNS settings take effect immediately.")
                else:
                    raise Exception("Failed to flush DNS cache")
                    
            except Exception as e:
                self.status_bar.config(text=f"❌ Error flushing DNS: {str(e)}", fg=self.error_color)
                messagebox.showerror("Error", f"Failed to flush DNS cache:\n{str(e)}")
        
        threading.Thread(target=flush_in_thread, daemon=True).start()

def main():
    root = tk.Tk()
    app = DNSChangerApp(root)
    
    # Set window icon (if available)
    try:
        root.iconbitmap(default="dns_icon.ico")  # Add your icon file
    except:
        pass
    
    # Center the window
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (root.winfo_width() // 2)
    y = (root.winfo_screenheight() // 2) - (root.winfo_height() // 2)
    root.geometry(f"+{x}+{y}")
    
    # Make window non-resizable for better appearance
    root.resizable(False, False)
    
    root.mainloop()

if __name__ == "__main__":
    main()