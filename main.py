import argparse
import sys
import os

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "src"))

from agent import Agent

def main():
    parser = argparse.ArgumentParser(description="Sili: Your Lightweight Local Autonomous Agent")
    parser.add_argument("goal", type=str, nargs="+", help="The goal you want the agent to achieve.")
    parser.add_argument("--image", type=str, action="append", help="Path to an image to provide to the vision model (can be used multiple times).")
    parser.add_argument("--text-model", type=str, default="llama3.1", help="Ollama text model to use (default: llama3.1)")
    parser.add_argument("--vision-model", type=str, default="llama3.2-vision", help="Ollama vision model to use (default: llama3.2-vision)")
    
    args = parser.parse_args()
    
    goal_string = " ".join(args.goal)
    
    print("==================================================")
    print("                 OPENCLAW                         ")
    print("==================================================")
    print(f"Goal: {goal_string}")
    print(f"Text Model: {args.text_model}")
    if args.image:
        print(f"Vision Images: {len(args.image)} attached")
        print(f"Vision Model: {args.vision_model}")
    print("==================================================\n")

    try:
        agent = Agent(text_model=args.text_model, vision_model=args.vision_model)
        result = agent.run(goal=goal_string, image_paths=args.image)
        
        print("\n==================================================")
        print("                 FINAL RESULT                     ")
        print("==================================================")
        print(result)
        
    except Exception as e:
        print(f"\n[CRITICAL ERROR] Failed to run Agent: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
