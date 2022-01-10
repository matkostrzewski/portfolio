using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class Game : MonoBehaviour
{

    private float bounceBoxOffset;
    private float groundOffset;

    private float bounceBoxSize;
    private float groundSize;

    public Sprite leftBlock;
    public Sprite centerBlock;
    public Sprite rightBlock;
    public Sprite singleBlock;
    public PhysicsMaterial2D bounceMaterial;
    GameObject player;

    public int phase;
    int[] platforms = { 0, 1, 2, 4};

    private float minX = -10.75f;
    private float maxX = 10.5f;
    private float maxY = 3.0f;

    // Start is called before the first frame update
    void Start()
    {
        player = GameObject.Find("Player");
        bounceBoxOffset = -0.09676695f;
        bounceBoxSize = 0.8f;

        groundOffset = 0.4f;
        groundSize = 0.20f;
        CrerateBlock();
        phase = 0;

    }

    // Update is called once per frame
    void Update()
    {
        
    }

    void CrerateBlock()
    {
        int len = Phase(phase);
        int start = localStart(len);
        int end = len + start;

        GameObject newBlock = new GameObject("nextPlatform");
        newBlock.tag = "platform";
        int leftOrRight = Random.Range(0, 100);
        float xBlock = 0.0f;
        if (player.transform.position.x < -6.3f)
        {
            leftOrRight = 51;
        }
        else if (player.transform.position.x > 6.3f)
        {
            leftOrRight = 49;
        }
        if (leftOrRight < 50)
        {
            float minR = 4.0f;
            if(len == 4)
            {
                minR = 6.0f;
            }
            xBlock = Random.Range(player.transform.position.x - minR, player.transform.position.x - 7.0f);
            if (xBlock < minX)
            {
                xBlock = minX;
            }
        }
        else
        {
            float minR = 4.0f;
            if (len == 4)
            {
                minR = 6.0f;
            }
            xBlock = Random.Range(player.transform.position.x + minR, player.transform.position.x + 7.0f);
            if (xBlock > maxX)
            {
                xBlock = maxX;
            }
        }
        newBlock.transform.position = new Vector3(
                xBlock,
                Random.Range(player.transform.position.y + 1.0f, player.transform.position.y + maxY),
                15f
            );

        for (int i = start; i <= len + start; i++)
        {
            GameObject child = new GameObject();
            child.transform.SetParent(newBlock.transform);
            float xPos = newBlock.transform.position.x;
            if (start == 0 && len == 0)
            {
                SpriteRenderer sp = child.AddComponent<SpriteRenderer>() as SpriteRenderer;
                sp.sprite = singleBlock;
                child.transform.localPosition = new Vector3(i, 0.0f, 15.0f);
            }
            else
            {
                if (i == start)
                {
                    SpriteRenderer sp = child.AddComponent<SpriteRenderer>() as SpriteRenderer;
                    sp.sprite = leftBlock;
                    child.transform.localPosition = new Vector3(i, 0.0f, 15.0f);
                }
                else if (i != end)
                {
                    SpriteRenderer sp = child.AddComponent<SpriteRenderer>() as SpriteRenderer;
                    sp.sprite = centerBlock;
                    child.transform.position = new Vector3(xPos, 0.0f, 15.0f);
                    child.transform.localPosition = new Vector3(i, 0.0f, 15.0f);
                }
                else
                {
                    SpriteRenderer sp = child.AddComponent<SpriteRenderer>() as SpriteRenderer;
                    sp.sprite = rightBlock;
                    child.transform.localPosition = new Vector3(i, 0.0f, 15.0f);
                }
            }
        }
        newBlock.layer = 8;
        float offset = 0.0f;
        if(len == 1)
        {
            offset = 0.5f;
        }
        BoxCollider2D ground2d = newBlock.AddComponent<BoxCollider2D>() as BoxCollider2D;
        ground2d.size = new Vector2(len + 1, groundSize);
        ground2d.offset = new Vector2(offset, groundOffset);

        BoxCollider2D bounce2d = newBlock.AddComponent<BoxCollider2D>() as BoxCollider2D;
        bounce2d.size = new Vector2(len + 1, bounceBoxSize);
        bounce2d.offset = new Vector2(offset, bounceBoxOffset);

        bounce2d.sharedMaterial = bounceMaterial;

        BoxCollider2D triggerScore = newBlock.AddComponent<BoxCollider2D>() as BoxCollider2D;
        triggerScore.size = new Vector2((float)len + 1, 0.25f);
        triggerScore.offset = new Vector2(offset, 0.55f);
        triggerScore.isTrigger = true;
    }

    int Phase(int phase)
    {
        int min = 0;
        int max = 2;
        if (phase == 0)
        {
            min = 2;
            max = 4;
        }
        if (phase == 1)
        {
            min = 2;
            max = 3;
        }
        if (phase == 2)
        {
            min = 0;
            max = 2;
        }
        int rng = 0;
        rng = Random.Range(min, max);
        return platforms[rng];
    }
    int localStart(int len)
    {
        int startPos = 0;
        if (len == 4)
        {
            startPos = -2;
        }
        else if(len == 2)
        {
            startPos = -1;
        }
        return startPos;
    }
    public void nextPhase()
    {
        phase += 1;
    }
}
