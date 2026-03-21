"""
Machine learning models for stock price prediction
Includes RandomForest and LSTM placeholder
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from config import LAG_FEATURES, N_ESTIMATORS, RANDOM_STATE


class LSTMModel:
    """
    Placeholder for LSTM model implementation
    
    TODO: Implement LSTM model using TensorFlow/Keras
    This class is designed for future upgrade from RandomForest to LSTM
    """
    
    def __init__(self, units=50, layers=2):
        """
        Initialize LSTM model placeholder
        
        Args:
            units (int): Number of LSTM units
            layers (int): Number of LSTM layers
        """
        self.units = units
        self.layers = layers
        self.model = None
        self.is_trained = False
        
        print(f"[PLACEHOLDER] LSTM model initialized with {units} units, {layers} layers")
    
    def build_model(self, input_shape):
        """
        Build LSTM model architecture
        
        TODO: Implement with TensorFlow/Keras
        Example:
            from tensorflow.keras.models import Sequential
            from tensorflow.keras.layers import LSTM, Dense, Dropout
            
            model = Sequential()
            model.add(LSTM(units=self.units, return_sequences=True, input_shape=input_shape))
            model.add(Dropout(0.2))
            model.add(LSTM(units=self.units, return_sequences=False))
            model.add(Dropout(0.2))
            model.add(Dense(1))
            model.compile(optimizer='adam', loss='mse')
            self.model = model
        """
        print(f"[PLACEHOLDER] Building LSTM model with input shape: {input_shape}")
        # TODO: Implement actual LSTM model
        pass
    
    def train(self, X, y, epochs=50, batch_size=32):
        """
        Train LSTM model
        
        TODO: Implement training logic
        """
        print(f"[PLACEHOLDER] Training LSTM model for {epochs} epochs")
        # TODO: Implement actual training
        self.is_trained = True
    
    def predict(self, X):
        """
        Make predictions with LSTM model
        
        TODO: Implement prediction logic
        """
        if not self.is_trained:
            raise ValueError("Model must be trained before making predictions")
        
        print("[PLACEHOLDER] LSTM prediction")
        # TODO: Implement actual prediction
        return np.zeros(len(X))


def create_lag_features(df, n_lags=LAG_FEATURES):
    """
    Create lag features for time series prediction
    
    Args:
        df (pd.DataFrame): DataFrame with 'Close' column
        n_lags (int): Number of lag features to create
    
    Returns:
        pd.DataFrame: DataFrame with lag features
    """
    df = df.copy()
    
    # Create lag features
    for i in range(1, n_lags + 1):
        df[f'Close_lag_{i}'] = df['Close'].shift(i)
    
    # Drop rows with NaN values from lag creation
    df = df.dropna()
    
    return df


def prepare_features(df):
    """
    Prepare feature matrix and target variable
    
    Args:
        df (pd.DataFrame): DataFrame with indicators and lag features
    
    Returns:
        tuple: (X, y) feature matrix and target vector
    """
    # Feature columns
    feature_columns = ['SMA', 'EMA', 'RSI', 'Momentum'] + [f'Close_lag_{i}' for i in range(1, LAG_FEATURES + 1)]
    
    # Check if all feature columns exist
    missing_cols = [col for col in feature_columns if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Missing feature columns: {missing_cols}")
    
    X = df[feature_columns]
    y = df['Close']
    
    return X, y


def train_random_forest(df):
    """
    Train RandomForest model for price prediction
    
    Args:
        df (pd.DataFrame): DataFrame with indicators
    
    Returns:
        tuple: (model, X, y) trained model and data
    """
    # Create lag features
    df_with_lags = create_lag_features(df)
    
    # Prepare features
    X, y = prepare_features(df_with_lags)
    
    # Split data (use last row for prediction)
    X_train = X.iloc[:-1]
    y_train = y.iloc[:-1]
    
    # Train model
    model = RandomForestRegressor(
        n_estimators=N_ESTIMATORS,
        random_state=RANDOM_STATE,
        n_jobs=-1
    )
    
    model.fit(X_train, y_train)
    
    # Calculate training score
    train_score = model.score(X_train, y_train)
    print(f"RandomForest trained with R² score: {train_score:.4f}")
    
    return model, X, y


def predict_next_price(model, df):
    """
    Predict the next closing price
    
    Args:
        model: Trained RandomForest model
        df (pd.DataFrame): DataFrame with indicators
    
    Returns:
        float: Predicted next price
    """
    # Create lag features
    df_with_lags = create_lag_features(df)
    
    # Get the last row for prediction
    last_row = df_with_lags.iloc[[-1]]
    
    # Prepare features
    X_pred, _ = prepare_features(last_row)
    
    # Predict
    predicted_price = model.predict(X_pred)[0]
    
    return predicted_price


def get_feature_importance(model, df):
    """
    Get feature importance from trained model
    
    Args:
        model: Trained RandomForest model
        df (pd.DataFrame): DataFrame with indicators
    
    Returns:
        dict: Dictionary mapping feature names to importance scores
    """
    # Create lag features to get feature names
    df_with_lags = create_lag_features(df)
    X, _ = prepare_features(df_with_lags)
    
    # Get feature importance
    importance = model.feature_importances_
    feature_names = X.columns
    
    return dict(zip(feature_names, importance))


if __name__ == "__main__":
    # Test the models
    from data_loader import get_stock_data
    from analytics import add_all_indicators
    
    # Load and prepare data
    df = get_stock_data("AAPL")
    df = add_all_indicators(df)
    
    # Train RandomForest
    print("\n=== RandomForest Model ===")
    model, X, y = train_random_forest(df)
    predicted = predict_next_price(model, df)
    
    current_price = df['Close'].iloc[-1]
    print(f"\nCurrent Price: ${current_price:,.2f}")
    print(f"Predicted Price: ${predicted:,.2f}")
    print(f"Change: {((predicted - current_price) / current_price) * 100:.2f}%")
    
    # Feature importance
    print("\nFeature Importance:")
    importance = get_feature_importance(model, df)
    for feature, score in sorted(importance.items(), key=lambda x: x[1], reverse=True):
        print(f"  {feature}: {score:.4f}")
    
    # Test LSTM placeholder
    print("\n=== LSTM Model (Placeholder) ===")
    lstm = LSTMModel(units=50, layers=2)
    lstm.build_model((60, 5))