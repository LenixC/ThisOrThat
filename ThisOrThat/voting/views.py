from django.shortcuts import render
from django.http import HttpResponseRedirect
from supabase import create_client, Client
from django.conf import settings
from dotenv import load_dotenv
import os
import random

load_dotenv()

supabase: Client = create_client(
            os.getenv('DATABASE_URL'),
            os.getenv('API_KEY'),
        )

def calculate_elo(winner_rating, loser_rating, k_factor=32):
    expected_win = 1 / (1 + 10 ** ((loser_rating - winner_rating) / 400))
    new_winner_rating = winner_rating + k_factor * (1 - expected_win)
    new_loser_rating = loser_rating + k_factor * (0 - (1 - expected_win))
    return new_winner_rating, new_loser_rating

def vote(request):
    if request.method == 'POST':
        winner = request.POST.get('winner')
        loser = request.POST.get('loser')
        print("winner: ", winner)
        print("loser: ", loser)
        
        winner_elo = supabase.table('restaurants')\
                .select("ELO")\
                .eq("CHAIN", winner)\
                .execute().data[0]['ELO']
        loser_elo = supabase.table('restaurants')\
                .select("ELO")\
                .eq("CHAIN", loser)\
                .execute().data[0]['ELO']
        
        new_winner_rating, new_loser_rating = calculate_elo(winner_elo, loser_elo)
        print("New Winner Rating: ", new_winner_rating)
        print("New Loser Rating: ", new_loser_rating)
        
        response_winner = (
                supabase.table('restaurants')
                .update({'ELO': new_winner_rating})
                .eq('CHAIN', winner).execute()
        )
        response_loser = (
                supabase.table('restaurants')
                .update({'ELO': new_loser_rating})
                .eq('CHAIN', loser).execute()
        )

        
        return HttpResponseRedirect('')
    
    else:
        # Get two random restaurants
        restaurants = supabase.table("restaurants").select("*").execute().data
        if len(restaurants) < 2:
            return render(request, 'voting/vote.html', 
                    {'error': 'Not enough restaurants'})
        
        choice1, choice2 = random.sample(restaurants, 2)
        return render(request, 'voting/vote.html', 
                {'choice1': choice1['CHAIN'], 'choice2': choice2['CHAIN']})
