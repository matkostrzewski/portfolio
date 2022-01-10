using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;

public class Player : MonoBehaviour
{

    public float jumpStreangth = 0.0f;
    public bool isGrounded;
    public bool isFlying;
    public float jumpDirectory;

    private Rigidbody2D rb;
    public LayerMask groundMask;
    public Image powerImg;
    public Slider slid;
    public Gradient gradient;
    public GameObject menuGo;
    private bool gameActive = true;

    public float horizontalInput;
    private int score = 0;
    public UnityEngine.UI.Text scoreText;

    private Vector3 lastPos;
    private float jumpSize = 0.6f;

    Animator animator;

    // Start is called before the first frame update
    void Start()
    {
        rb = gameObject.GetComponent<Rigidbody2D>();
        animator = GetComponent<Animator>();
        scoreText.text = score.ToString();
        menuGo.SetActive(false);

    }
    // Update is called once per frame
    void Update()
    {
        if (gameActive)
        {
            horizontalInput = Input.GetAxis("Horizontal");
            CheckGround();
            if (isGrounded)
            {
                isFlying = false;
                animator.SetBool("jumping", false);
            }
            else
            {
                animator.Play("jump");
                animator.SetBool("jumping", true);
                isFlying = true;
            }
            //force stop, no sliding
            if ((rb.velocity.x > 0.0f || rb.velocity.x < 0.0f) && rb.velocity.y == 0.0f)
            {
                if (isGrounded)
                {
                    rb.velocity = new Vector2(0.0f, 0.0f);
                }
            }
            if (Input.GetButton("Fire1") && isGrounded == true && slid.value < 100.0f)
            {
                jumpStreangth += 0.25f;
                slid.value += 0.8f;
                powerImg.color = gradient.Evaluate(slid.normalizedValue);

            }
            if (Input.GetButtonUp("Fire1"))
            {
                // canJump = false;
                lastPos = gameObject.transform.position;
                rb.velocity = new Vector2(jumpStreangth * jumpSize * (jumpDirectory / 2), jumpStreangth * jumpSize);
                ResetBar();
                if (rb.velocity.y != 0.0f)
                {
                    isFlying = true;
                }
                GetComponents<AudioSource>()[0].Play();
            }
            if (Input.GetButtonUp("Fire1") && isGrounded == true)
            {
                jumpStreangth = 0.0f;
            }
            if (Input.GetButton("Fire2"))
            {
                LastPosition();
            }
            if (horizontalInput > 0 && isGrounded == true)
            {
                //jump right
                jumpDirectory = 1.0f;
                animator.SetFloat("speed", 1.0f);
                transform.rotation = new Quaternion(0.0f, 0.0f, 0.0f, 0.0f);

            }
            else if (horizontalInput < 0 && isGrounded == true)
            {
                //jump left
                jumpDirectory = -1.0f;
                animator.SetFloat("speed", 1.0f);
                transform.rotation = new Quaternion(0.0f, 180.0f, 0.0f, 0.0f);

            }
            else if (horizontalInput == 0 && isGrounded == true)
            {
                jumpDirectory = 0.0f;
                animator.SetFloat("speed", 0.0f);
            }
        }
        else
        {
            menuGo.SetActive(true);
        }

    }

    void LastPosition()
    {
        gameObject.transform.position = lastPos;
    }


    void OnTriggerEnter2D(Collider2D col)
    {
        Debug.Log(col.tag);
        if (col.tag == "Finish")
        {
            //gameActive = false;
        }
        else
        {
            BoxCollider2D[] colids = col.GetComponents<BoxCollider2D>();
            Destroy(colids[2]);
            GameObject GM = GameObject.Find("Platforms");
            GM.SendMessage("CrerateBlock");
            score += 1;
            scoreText.text = score.ToString();
            if (score == 8)
            {
                GameObject.Find("Platforms").GetComponent<Game>().nextPhase();
            }
            if (score == 16)
            {
                GameObject.Find("Platforms").GetComponent<Game>().nextPhase();
            }
        }

    }

    private void OnCollisionEnter2D(Collision2D collision)
    {
        GetComponents<AudioSource>()[1].Play();
    }

    void ResetBar()
    {
        slid.value = 0.0f;
        powerImg.color = gradient.Evaluate(slid.normalizedValue);
    }

    void CheckGround()
    {
        //checking ground and setting canJump 
        isGrounded = Physics2D.OverlapBox(new Vector2(gameObject.transform.position.x, gameObject.transform.position.y - 0.5f), new Vector2(0.9f, 0.4f), 0f, groundMask);
    }
}
