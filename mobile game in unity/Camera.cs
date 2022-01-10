using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class Camera : MonoBehaviour
{
    // Start is called before the first frame update
    GameObject player;
    public UnityEngine.UI.Text scoreText;
    int prevScore = 0;
    Vector3 posCap;
    void Start()
    {
        player = GameObject.Find("Player");
        prevScore = int.Parse(scoreText.text);
        

}

    // Update is called once per frame
    void Update()
    {
        if(player.transform.position.y > 5.0f && prevScore < int.Parse(scoreText.text))
        {
            //posCap = new Vector3(gameObject.transform.position.x, player.transform.position.y, gameObject.transform.position.z);
            transform.position = new Vector3(gameObject.transform.position.x, player.transform.position.y, gameObject.transform.position.z);

            prevScore++;
        }
        /*if(transform.position.y < posCap.y)
        {
            transform.position = transform.position += new Vector3(0.0f, 0.02f, 0.0f);
        }*/
        GameObject[] platforms = GameObject.FindGameObjectsWithTag("platform");
        if(platforms.Length > 10)
        {
            for (int i = 0; i <= 4; i++) {
                Destroy(platforms[i]);
            }
        }

    }
}
