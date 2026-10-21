import './style.css';
import { mountEstimator } from './estimator';

const estimatorRoot = document.getElementById('estimator-root');
if (estimatorRoot) mountEstimator(estimatorRoot);
