import React, { Component } from 'react';


class Row extends Component {

    render() {
        return ( 
            <tr>
                <td>{this.props.index + 1}</td>
                <td>{this.props.data.url}</td>
                <td></td>
                <td>{this.props.data.status}</td>
            </tr>
        )
    }
}

class UrlTable extends Component {
    constructor(props) {
        super(props) ;
        this.status = { 
            update: false,
            data: this.props.data
        }
    }

    render() {
        return (
            <div className="people">
                <table>
                    <caption>List of Url</caption>
                    <thead>
                        <tr>
                            <th>url</th>
                            <th>status</th>
                            <th>timestamp</th>
                            <th>action</th>
                        </tr>
                    </thead>
                    <tbody>
                        {this.status.data.map((data, index) => <Row data={data} index={index}/>)}
                    </tbody>
                </table>
            </div> 
        )
    }
}

export default UrlTable ;
