// Recon Template: Replace with your recon logic
use std::env;
fn main() {
    let args: Vec<String> = env::args().collect();
    if args.len() < 2 {
        println!("Usage: recon_template <target>");
        return;
    }
    println!("[Recon] Scanning {}...", args[1]);
    // Add recon logic here
}
