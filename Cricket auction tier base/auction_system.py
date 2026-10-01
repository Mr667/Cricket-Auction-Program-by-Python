import json
import random
import os
import re

def parse_amount(amt_str):
    """Parses amount strings like '1cr', '50k', '1.5L', '10,000' into integers."""
    amt_str = str(amt_str).lower().replace(",", "").replace("₹", "").strip()
    try:
        if amt_str.endswith('k'):
            return int(float(amt_str[:-1]) * 1000)
        elif 'lakh' in amt_str or amt_str.endswith('l'):
            val = amt_str.replace('lakhs', '').replace('lakh', '').replace('l', '').strip()
            return int(float(val) * 100000)
        elif 'cr' in amt_str or 'crore' in amt_str or amt_str.endswith('c'):
            val = amt_str.replace('crores', '').replace('crore', '').replace('cr', '').replace('c', '').strip()
            return int(float(val) * 10000000)
        else:
            return int(float(amt_str))
    except ValueError:
        return None

def format_currency(amount):
    """Formats integer to Indian currency format with commas."""
    # Custom format for Indian numbering system can be complex, using standard comma separation for simplicity
    # but we can do a quick regex for Indian style if needed. Standard thousands separator is fine for now.
    s, *d = str(amount).partition(".")
    r = ",".join([s[x-2:x] for x in range(-3, -len(s), -2)][::-1] + [s[-3:]])
    return f"₹{r}"

class CricketAuction:
    def __init__(self):
        self.members = {}
        self.players = []
        self.unsold_players = []
        self.current_player = None
        self.current_bid = 0
        self.current_bidder = None
        self.base_price = 50000
        self.starting_budget = 1000000

    def load_data(self, members_list, players_list):
        self.members = {
            m: {"balance": self.starting_budget, "squad": []} for m in members_list
        }
        self.players = players_list.copy()
        self.unsold_players = []
        self.current_player = None
        self.current_bid = 0
        self.current_bidder = None

    def get_base_price(self, tier):
        tier_norm = str(tier).strip().capitalize()
        return 100000 if tier_norm == "Diamond" else 50000

    def initialize(self):
        print("\n🧹 Initializing new auction...")
        
        # In a real app, you might load from a file. Here we prompt or use dummy data.
        print("For this interactive system, we will load sample data.")
        sample_members = [f"Member_{i}" for i in range(1, 13)]
        sample_players = [
            {"name": "Virat Kohli", "role": "Batsman", "tier": "Diamond"},
            {"name": "Jasprit Bumrah", "role": "Bowler", "tier": "Diamond"},
            {"name": "Hardik Pandya", "role": "All-rounder", "tier": "Diamond"},
            {"name": "MS Dhoni", "role": "Wicketkeeper", "tier": "Diamond"},
            {"name": "Rashid Khan", "role": "Bowler", "tier": "Standard"},
            {"name": "Ben Stokes", "role": "All-rounder", "tier": "Standard"}
        ]
        
        self.load_data(sample_members, sample_players)
        print("✅ System Initialized: 12 Members, Sample Players loaded. Budget set to 10 Lakhs each.")
        print("Type '/next_standard' or '/next_diamond [Name]' to begin drawing players.\n")

    def next_standard(self):
        if self.current_player:
            print(f"⚠️ Resolve the current player ({self.current_player['name']}) first using /sold or /unsold.")
            return

        # Find standard players
        standard_pool = [p for p in self.players if str(p.get("tier", "Standard")).strip().capitalize() != "Diamond"]
        
        if not standard_pool:
            print("🏁 No more Standard players left in the main pool.")
            return

        self.current_player = random.choice(standard_pool)
        self.players.remove(self.current_player)
        self.base_price = 50000
        self.current_bid = self.base_price
        self.current_bidder = None

        print(f"\n=====================================")
        print(f"🏏 UP FOR AUCTION (STANDARD) 🏏")
        print(f"Name: {self.current_player['name']}")
        print(f"Role: {self.current_player['role']}")
        print(f"Tier: Standard")
        print(f"💰 BASE PRICE: {format_currency(self.base_price)}")
        print(f"=====================================")
        print("The floor is open! Use: /bid [Member Name] [Amount]")

    def next_diamond(self, player_name):
        if self.current_player:
            print(f"⚠️ Resolve the current player ({self.current_player['name']}) first using /sold or /unsold.")
            return

        # Find the specific diamond player
        player_name_lower = player_name.lower().strip()
        found_player = None
        for p in self.players:
            if str(p.get("tier", "Standard")).strip().capitalize() == "Diamond" and p['name'].lower().strip() == player_name_lower:
                found_player = p
                break
                
        if not found_player:
            print(f"❌ Could not find Diamond player named '{player_name}' in the available pool.")
            return

        self.current_player = found_player
        self.players.remove(self.current_player)
        self.base_price = 100000
        self.current_bid = self.base_price
        self.current_bidder = None

        print(f"\n=====================================")
        print(f"💎 UP FOR AUCTION (DIAMOND) 💎")
        print(f"Name: {self.current_player['name']}")
        print(f"Role: {self.current_player['role']}")
        print(f"Tier: Diamond")
        print(f"💰 BASE PRICE: {format_currency(self.base_price)}")
        print(f"=====================================")
        print("The floor is open! Use: /bid [Member Name] [Amount]")

    def bid(self, member_name, amount_str):
        if not self.current_player:
            print("⚠️ No player is currently on the floor. Type '/next' to draw a player.")
            return

        if member_name not in self.members:
            print(f"❌ Invalid member name: {member_name}")
            return

        amount = parse_amount(amount_str)
        if amount is None:
            print(f"❌ Could not parse amount '{amount_str}'. Try formats like '50k', '1.5cr', '20000'.")
            return

        if self.members[member_name]["balance"] < 50000:
            print(f"❌ {member_name} has less than ₹50,000 remaining and can no longer participate in the auction.")
            return

        if amount <= self.current_bid and self.current_bidder is not None:
            print(f"❌ Bid must be higher than current bid of {format_currency(self.current_bid)}")
            return
            
        if amount < self.base_price:
            print(f"❌ Bid cannot be lower than base price of {format_currency(self.base_price)}")
            return

        if amount > self.members[member_name]["balance"]:
            print(f"❌ Insufficient funds! {member_name} only has {format_currency(self.members[member_name]['balance'])} remaining.")
            return

        self.current_bid = amount
        self.current_bidder = member_name
        print(f"✅ BID ACCEPTED: {member_name} bids {format_currency(self.current_bid)} for {self.current_player['name']}!")

    def sold(self, member_name=None, amount_str=None):
        if not self.current_player:
            print("⚠️ No player is currently on the floor.")
            return

        if member_name and amount_str:
            # Forced sold command overriding current bid
            amount = parse_amount(amount_str)
            if member_name not in self.members:
                print(f"❌ Invalid member name: {member_name}")
                return
            self.current_bidder = member_name
            self.current_bid = amount
        elif not self.current_bidder:
            print("❌ No bids have been made yet! Either place a /bid or use /sold [Member] [Amount]")
            return

        final_member = self.current_bidder
        final_amount = self.current_bid

        if final_amount > self.members[final_member]["balance"]:
             print(f"❌ {final_member} cannot afford this! Balance: {format_currency(self.members[final_member]['balance'])}")
             return

        self.members[final_member]["balance"] -= final_amount
        
        player_record = {
            "name": self.current_player['name'],
            "role": self.current_player['role'],
            "tier": self.current_player.get('tier', 'Standard'),
            "price": final_amount
        }
        self.members[final_member]["squad"].append(player_record)

        print(f"\n🎉 SOLD! 🎉")
        print(f"{self.current_player['name']} is sold to {final_member} for {format_currency(final_amount)}!")
        print(f"{final_member}'s remaining balance: {format_currency(self.members[final_member]['balance'])}")
        
        # Reset floor
        self.current_player = None
        self.current_bid = 0
        self.current_bidder = None

    def unsold(self):
        if not self.current_player:
            print("⚠️ No player is currently on the floor.")
            return

        print(f"❌ UNSOLD! {self.current_player['name']} returns to the unsold pool.")
        self.unsold_players.append(self.current_player)
        
        # Reset floor
        self.current_player = None
        self.current_bid = 0
        self.current_bidder = None

    def status(self):
        print("\n📊 AUCTION STATUS 📊")
        print(f"{'Member Name':<15} | {'Remaining Balance':<15} | {'Players Bought':<15}")
        print("-" * 52)
        for member, data in self.members.items():
            print(f"{member:<15} | {format_currency(data['balance']):<15} | {len(data['squad']):<15}")
        print("-" * 52)

    def final_summary(self):
        print("\n🏆 FINAL AUCTION SUMMARY 🏆\n")
        for member, data in self.members.items():
            print(f"=====================================")
            print(f"🔥 {member.upper()} SQUAD")
            print(f"Remaining Budget: {format_currency(data['balance'])}")
            print(f"Total Players: {len(data['squad'])}")
            print("-" * 37)
            for p in data['squad']:
                print(f"- {p['name']} ({p['role']} - {p.get('tier', 'Standard')}) : {format_currency(p['price'])}")
            print(f"=====================================\n")

def main():
    auction = CricketAuction()
    print("Welcome to the Ultimate Cricket Auction System!")
    print("Available Commands:")
    print("  /initialize")
    print("  /next_standard")
    print("  /next_diamond [Player Name]")
    print("  /bid [Member Name] [Amount]")
    print("  /sold (or /sold [Member Name] [Amount])")
    print("  /unsold")
    print("  /status")
    print("  /final_summary")
    print("  /exit")

    while True:
        try:
            cmd_input = input("\nAuctionMaster> ").strip()
            if not cmd_input:
                continue
                
            parts = cmd_input.split()
            command = parts[0].lower()

            if command == "/exit":
                print("Exiting Auction Master. Goodbye!")
                break
            elif command == "/initialize":
                auction.initialize()
            elif command == "/next_standard":
                auction.next_standard()
            elif command == "/next_diamond":
                if len(parts) >= 2:
                    player_name = " ".join(parts[1:])
                    auction.next_diamond(player_name)
                else:
                    print("Usage: /next_diamond [Player Name]")
            elif command == "/bid":
                if len(parts) >= 3:
                    member_name = parts[1]
                    amount_str = " ".join(parts[2:])
                    auction.bid(member_name, amount_str)
                else:
                    print("Usage: /bid [Member Name] [Amount]")
            elif command == "/sold":
                if len(parts) >= 3:
                    member_name = parts[1]
                    amount_str = " ".join(parts[2:])
                    auction.sold(member_name, amount_str)
                else:
                    auction.sold()
            elif command == "/unsold":
                auction.unsold()
            elif command == "/status":
                auction.status()
            elif command == "/final_summary":
                auction.final_summary()
            else:
                print("❌ Unknown command. Please use one of the valid commands.")
        except KeyboardInterrupt:
            print("\nExiting Auction Master. Goodbye!")
            break
        except Exception as e:
            print(f"An error occurred: {e}")

if __name__ == '__main__':
    main()
