import React from 'react';
import RaisedButton from 'material-ui/RaisedButton';
import {Card, CardActions, CardHeader, CardMedia, CardTitle, CardText} from 'material-ui/Card';
import { fireSentryGun, panSentryRight, panSentryLeft } from 'utils/http_functions'
const styles = {
  nonTransformedLabel: {
    'text-transform': 'none'
  },
  button: {
    margin: 12,
  },
  firebutton: {
    margin: 12,
    'background-color': 'red',
  },
  sentryFeed: {
      'width': '70%',
      'minWidth': '50%',
      height: 'auto',
  }
};

export const Home = () =>
    <section>
        <div className="container text-center">
            <CardMedia
                overlay={<CardTitle title="Live sentry feed"/>}>
                <div style>
                <img style={styles.sentryFeed} src="http://rsukuma-raspberrypi.local:5000/sentry_gun_camera"/>
                </div>
            </CardMedia>
        </div>
        <div className="text-center">
            <RaisedButton onClick={panSentryLeft} label="<<<<< Pan left" primary={true} style={styles.button} />
            <RaisedButton onClick={fireSentryGun} label="Fire" secondary={true}/>
            <RaisedButton onClick={panSentryRight} label="Pan Right >>>>>>" primary={true} style={styles.button} />
        </div>
        <div>
        </div>
    </section>;
