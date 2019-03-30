import React, { Component } from 'react';
import TableRow from "./TableRow.js"
import {UrlModel, VideoMetaData, MapVideoModelToAppModel} from "./model.js"

const ErrorMsg = ({msg}) => <div className="error">{msg}</div>

class UrlTable extends Component {
    constructor(props) {
        super(props) ;
        this.state = { 
            data: this.props.data,
            error: false
        }

        this.errorMsg = ""
        this.onRemoveUrl = this.onRemoveUrl.bind(this)
        this.addUrl = this.addUrl.bind(this)
    
    }

    render() {
        return (
            <div>        
                <div className="people">
                    <table>
                        <thead>
                            <tr>
                                <th>Id</th>
                                <th>Url</th>
                                <th>Timestamp</th>
                                <th>Status</th>
                                <th>Action</th>
                            </tr>
                        </thead>
                        <tbody>
                            {this.state.data.map((data, index) => <TableRow key={data.uid} data={data} index={index} onRemoveUrl={this.onRemoveUrl}/>)}
                        </tbody>
                    </table>
                </div>
                {(this.state.error) ? <ErrorMsg msg={this.errorMsg}/> : <div />}
            </div> 
        )
    }

    componentDidUpdate(prevProps, prevState)
    {
        console.log("componentDidUpdate")
        console.log("this.state",this.state)
        if (this.state.error) {
            setTimeout(() => {this.setState({error: false})}, 3000)
        }
    }

    onRemoveUrl(index, video_id) {
        console.log("onRemoveUrl:"+video_id)
        var url = "http://localhost:5000/api/delete/"+video_id
        fetch(url)
        .then(res => res.json())
        .then(data => {
                if (!data.error) {
                    this.state.data.splice(index,1)
                    this.setState({data: this.props.data})
                } else {
                    // duplicated URL
                    this.errorMsg = "Can't delete video id:"+video_id
                    this.setState({error: true})
                }
            })
        .catch(error => console.log('Request failed', error))  
        
        console.log("state:", this.state)
    }


    addUrl(video_url) {
        console.log("adddUrl:"+video_url)
        // var lastId = this.props.data[this.props.data.length-1].uid 
        // this.props.data.push(UrlModel(lastId+1, video_url, "pending", new Date().getTime(), VideoMetaData()))
        // this.setState({data: this.props.data})

        var url = "http://localhost:5000/api/video?url="+video_url
        fetch(url, {method: "POST"})
        .then(res => res.json())
        .then(data => {
                if (!data.error) {
                    this.props.data.push(MapVideoModelToAppModel(data))
                    this.setState({data: this.props.data})
                } else {
                    // duplicated URL
                    this.errorMsg = "Duplicated URL : \n"+video_url
                    this.setState({error: true})
                }
            })
        .catch(error => console.log('Request failed', error))  

    }   
}

export default UrlTable ;
