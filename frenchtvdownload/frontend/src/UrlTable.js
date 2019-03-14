import React, { Component } from 'react';
import {UrlModel, VideoMetaData} from "./model.js"

const Item = ({classname, value, style}) => <td className={classname} style={style}>{value}</td>
const Button = ({classname, value, style, onClick}) => <button className={classname} style={style} onClick={onClick}>{value}</button>


class Row extends Component {
    constructor(props) {
        super(props) ;
        this.state = {
            status: this.props.data.status
        }

        this.onDownloadVideo = this.onDownloadVideo.bind(this)
        this.onCancelDownload = this.onCancelDownload.bind(this)
    }

    render() {

        var statusText, statusBgColor ;

        switch(this.state.status) {
            case "done":
                statusText = "Done" 
                statusBgColor = "Aquamarine" 
            break ;

            case "pending":
                statusText = "Pending"
                statusBgColor = "CornflowerBlue"
            break ;

            case "downloading":
                statusText = "..."
                statusBgColor = "Plum"
            break ;
            
            case "not_availabl":
                statusText = "Not Available"
                statusBgColor = "greenyellow"
            break ;

            default:
                statusText = "Unknown"
                statusBgColor = "red"
            break ;
        }

            return ( 
            <tr>
                <Item value={this.props.data.uid} />
                <Item classname="url" value={this.props.data.url} />
                <Item value={this.props.data.timestamp}/>
                <Item value={statusText} style={{background: statusBgColor}}/>
                <td>
                    {(this.state.status==="downloading") ? 
                        <Button value="Cancel" onClick={this.onCancelDownload}/> : <Button value="Remove" onClick={() => this.props.onRemoveUrl(this.props.index)}/>}
                    {(this.state.status==="pending") && <Button value="Download" onClick={this.onDownloadVideo}/>}
                </td>
            </tr>
        )
    }

    onDownloadVideo() {
        console.log("onDownloadVideo:",this.props.index)
    }

    onCancelDownload() {
        console.log("onCancelDownload:",this.props.index)
    }
}

class UrlEditor extends Component {
    constructor(props) {
        super(props)
        this.myRef = React.createRef();

        this.onChange = this.onChange.bind(this)

        this.state = {
            addUrlButtonEnable : false
        }
    }

    render() {
        return (
            <div className="editor">
                <label htmlFor="url" style={{width: '80%'}}>Url :
                    <input id="url" ref="_url" type="text" style={{width: '80%'}} onChange={evt => this.onChange(evt)}/>
                    <button disabled={!this.state.addUrlButtonEnable} onClick={()=> this.props.onAddUrl(this.refs._url.value)}>Add Url</button>
                </label>
            </div>
        )
    }

    onChange(evt) {
        if (this._isURL(evt.target.value)) {
            if (!this.state.addUrlButtonEnable)
            {
                this.setState({
                    addUrlButtonEnable : true
                })
            }
        }
        else {
            if (this.state.addUrlButtonEnable)
            {
                this.setState({
                    addUrlButtonEnable : false
                })
            }
        }
    }

    _isURL(str) {
        var pattern = new RegExp('^((ft|htt)ps?:\\/\\/)?'+ // protocol
        '((([a-z\\d]([a-z\\d-]*[a-z\\d])*)\\.)+[a-z]{2,}|'+ // domain name and extension
        '((\\d{1,3}\\.){3}\\d{1,3}))'+ // OR ip (v4) address
        '(\\:\\d+)?'+ // port
        '(\\/[-a-z\\d%@_.~+&:]*)*'+ // path
        '(\\?[;&a-z\\d%@_.,~+&:=-]*)?'+ // query string
        '(\\#[-a-z\\d_]*)?$','i'); // fragment locator
        return pattern.test(str);
      }    
}

class UrlTable extends Component {
    constructor(props) {
        super(props) ;
        this.state = { 
            data: this.props.data
        }

        this.onRemoveUrl = this.onRemoveUrl.bind(this)
        this.onAddUrl = this.onAddUrl.bind(this)
    }

    render() {
        return (
            <div>
                <UrlEditor onAddUrl={this.onAddUrl}/>
        
                <div className="people">
                    <table>
                        <caption>List of Url</caption>
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
                            {this.state.data.map((data, index) => <Row key={data.uid} data={data} index={index} onRemoveUrl={this.onRemoveUrl}/>)}
                        </tbody>
                    </table>
                </div>
                <div className="error">
                </div>
            </div> 
        )
    }

    onRemoveUrl(index) {
        console.log("onRemoveUrl:"+index)
        this.state.data.splice(index,1)
        this.setState({data: this.props.data})
        console.log("state:", this.state)
     }


    onAddUrl(url) {
        console.log("onAddUrl:"+url)
        var lastId = this.props.data[this.props.data.length-1].uid 
        this.props.data.push(UrlModel(lastId+1, url, "pending", 1551913200.0, VideoMetaData()))
        this.setState({data: this.props.data})
    }


    
}

export default UrlTable ;
