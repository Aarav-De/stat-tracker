import aiobungie
import requests
import pandas as pd
from datetime import datetime
import json

# kis#5363

API_KEY = '53fdf16d3fcd4ab684680be6a18073d2'

async def fetch_me(name: str, identifier: int, membership_number: int) -> None:
    client = aiobungie.Client(API_KEY)

    async with client.rest:
        memberships = await client.fetch_membership(name, identifier)

        # Iterate over all memberships.
        for membership in memberships:

            # Check the membership type.
            if membership_number == 1 and membership.type is aiobungie.MembershipType.XBOX:
                print(f"Found Xbox membership! {membership!s}")
            elif membership_number == 2 and membership.type is aiobungie.MembershipType.PSN:
                print(f"Found Playstation membership! {membership!s}")
            elif membership_number == 3 and membership.type is aiobungie.MembershipType.STEAM:
                print(f"Found Steam membership! {membership!s}")
            elif membership_number == 4 and membership.type is aiobungie.MembershipType.BLIZZARD:
                print(f"Found Blizzard membership! {membership!s}")
            else:
                continue

            # Fetch Destiny 1 stats
            url = f"https://www.bungie.net/d1/Platform/Destiny/Stats/Account/{membership_number}/{membership.id}/"
            headers = {
                'X-API-Key': API_KEY
            }
            
            response = requests.get(url, headers=headers)
            data = response.json()

            # Generate the file name
            current_date = datetime.now().strftime("%m-%d-%Y")
            file_name = f"{current_date} - {name} Stats.xlsx"
            file_name_txt = f"{current_date} - {name} Stats.txt"
            
            # Write the raw JSON data to a text file
            with open(file_name_txt, 'w') as f:
                json.dump(data, f, indent=4)
            print(f"Raw data saved to {file_name_txt}")

            # Extract and normalize the stats data
            pve_stats = data['Response']['mergedAllCharacters']['results']['allPvE']['allTime']
            pvp_stats = data['Response']['mergedAllCharacters']['results']['allPvP']['allTime']

            # Normalize each section separately
            pve_df = pd.json_normalize(pve_stats).transpose().reset_index()
            pvp_df = pd.json_normalize(pvp_stats).transpose().reset_index()

            # Rename columns for clarity
            pve_df.columns = ['PvE Stat', 'PvE Value']
            pvp_df.columns = ['PvP Stat', 'PvP Value']

            # Concatenate the DataFrames side-by-side
            combined_df = pd.concat([pve_df, pvp_df], axis=1)


            # Save the combined DataFrame to an Excel file
            combined_df.to_excel(file_name, index=False)
            print(f"Data saved to {file_name}")
            break
        else:
            print(f"No membership found for the specified type {membership_number}.")

if __name__ == "__main__":
    import asyncio

    # Input details
    membership_number = int(input("Enter the membership type (1: Xbox, 2: PSN, 3: Steam, 4: Blizzard): "))
    name = input("Enter the name: ")
    identifier = int(input("Enter the 4-digit identifier: "))

    asyncio.run(fetch_me(name, identifier, membership_number))
