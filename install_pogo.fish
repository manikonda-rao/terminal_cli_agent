#!/usr/bin/env fish
# Installation script for POGO - Terminal CLI Agent

function install_pogo --description "Install POGO fish function globally"
    # Get the current directory (where this script is located)
    set script_dir (pwd)
    set pogo_script "$script_dir/pogo.fish"
    
    # Check if pogo.fish exists
    if not test -f "$pogo_script"
        echo "❌ Error: pogo.fish not found in current directory"
        echo "Please run this script from the terminal_cli project directory"
        return 1
    end
    
    # Create fish functions directory if it doesn't exist
    set fish_functions_dir "$HOME/.config/fish/functions"
    if not test -d "$fish_functions_dir"
        echo "📁 Creating fish functions directory..."
        mkdir -p "$fish_functions_dir"
    end
    
    # Copy the pogo function to fish functions directory
    echo "📋 Installing POGO function..."
    cp "$pogo_script" "$fish_functions_dir/"
    
    # Set the POGO_PROJECT_DIR environment variable
    echo "🔧 Setting up environment variables..."
    set env_file "$HOME/.config/fish/config.fish"
    
    # Create config.fish if it doesn't exist
    if not test -f "$env_file"
        mkdir -p (dirname "$env_file")
        touch "$env_file"
    end
    
    # Add POGO_PROJECT_DIR to config.fish if not already present
    if not grep -q "POGO_PROJECT_DIR" "$env_file"
        echo "" >> "$env_file"
        echo "# POGO Terminal CLI Agent" >> "$env_file"
        echo "set -gx POGO_PROJECT_DIR \"$script_dir\"" >> "$env_file"
        echo "✅ Added POGO_PROJECT_DIR to fish config"
    else
        echo "ℹ️  POGO_PROJECT_DIR already configured"
    end
    
    # Reload fish configuration
    echo "🔄 Reloading fish configuration..."
    source "$env_file"
    
    echo ""
    echo "🎉 Pogo installation completed!"
    echo ""
    echo "Usage:"
    echo "  pogo                    # Launch the CLI agent"
    echo "  pogo --help            # Show help"
    echo "  pogo --project-root .  # Specify project root"
    echo ""
    echo "The POGO_PROJECT_DIR is set to: $script_dir"
    echo "You can change this by editing: $env_file"
    echo ""
    echo "🐟 Happy coding with Pogo!"
end

# Run installation if script is executed directly
if test (basename (status --current-filename)) = "install_pogo.fish"
    install_pogo
end
