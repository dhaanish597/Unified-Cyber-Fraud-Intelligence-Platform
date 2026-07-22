import React from 'react';
import RealTimeProcessingPipeline from './RealTimeProcessingPipeline';

export default function FusionLifecyclePipeline({ activeTxn, evaluation, websocketStages }) {
  return (
    <RealTimeProcessingPipeline 
      activeTxn={activeTxn} 
      evaluation={evaluation} 
      websocketStages={websocketStages} 
    />
  );
}
