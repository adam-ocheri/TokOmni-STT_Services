import {useEffect, useState} from 'react'
import axios from 'axios'

export default function MainPage() {

    const [filename, setFilename] = useState('');
    const [conversation, setConversation] = useState([]);

    useEffect(()=> {
        
    }, [])

    function onTextChanged(e) {
        setFilename(e.target.value)
    }

    function onTranscribeStart(){
        if (filename === "") return;

        const file = filename
        const url = "http://localhost:5000/request_transcription_work/";
        axios.get(url + file).then((response)=>{
            console.log("Got some response!")
            console.log(response)
            if(response?.data?.fullTranscript)
            {
                setConversation(response.data.fullTranscript);
            }
        }).catch((error) => {throw new Error(error)});
    }


    return (
        <div style={{display: 'flex', flexDirection: 'column', alignContent: 'center'}}>
            <input type={'text'} value={filename} onChange={(e)=>{onTextChanged(e)}}/>
            <button onClick={()=>{onTranscribeStart()}}>Start</button>

            {conversation.length > 0 && 
            <div>
                <h2>Conversation Result</h2>
                {conversation.map((item, idx) => (<div key={idx}>
                    item.speaker
                    <section style={{
                        background: item.speaker === "ServicePerson" ? 'purple' : 'orange',
                        display: 'flex',
                        flexDirection: 'column',
                        alignContent: 'center',
                        textAlign: 'center',
                        border: '2px solid black',
                        borderRadius: '12px',
                        paddingLeft: item.speaker === "ServicePerson" ? '100px' : '0',
                        paddingRight: item.speaker !== "ServicePerson" ? '100px' : '0',
                    }}>
                        <h3>{item.speaker}</h3>
                        <p>
                            {item.text}
                        </p>
                    </section>
                </div>))}
            </div>
            }
        </div>
    )
}
