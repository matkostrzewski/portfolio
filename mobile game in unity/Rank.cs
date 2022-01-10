using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;

public class Rank : MonoBehaviour
{
    public Text yourRank;
    public Text worldScore;

    // Start is called before the first frame update
    void Start()
    {
        int playerId = 1;
        yourRank.text = GetPlayerRank(playerId);
        worldScore.text = GetWorldRecordFromServer().ToString();
    }

    void SendScoreToServer(int score)
    {
        //check player is valid 
        //send score, player id and mac
    }

    void GenerateID()
    {
        //ask server for ID 
        // tilt/newplayerid
        //save on device id 
        //link mac to ID for security

    }

    int GetPlayerId()
    {
        //try get from device
        bool ask = true;
        if(ask == false)
        {
            GenerateID();
        }
        //try again
        int playerId = 0;
        return playerId;
    }

    int GetWorldRecordFromServer()
    {
        //get result from server
        return 0;
    }
    int GetPlayerHighestScore(int playerId)
    {
        //getResult from server if player is valid
        return 0;
    }

    string GetPlayerRank(int playerId)
    {
        //get rank if player is valid 
        return "";
    }

}
