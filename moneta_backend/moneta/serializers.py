from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from .models import Portfolio, Asset
from utils.brapi import fetch_brapi_data

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)  # p confirmar senha
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'cpf', 'phone', 'password', 'password2']
        extra_kwargs = {
            'username': {'required': True},
            'email': {'required': True},
        }

    def validate(self, attrs): # validacao de senha centralizado no serializer para garantir que a senha seja validada na etapa de criação do usuário
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "As senhas não conferem."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2') 
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)  # senha hashada
        user.save()
        return user

    
class PortfolioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Portfolio
        fields = ['id', 'name', 'created_at']
        read_only_fields = ['id', 'created_at']

    def create(self, validated_data):
        # portfolio será associado ao usuário logado - jwt
        user = self.context['request'].user
        return Portfolio.objects.create(user=user, **validated_data)


class AssetSerializer(serializers.ModelSerializer):
    """
    Serializer para criar assets em um portfólio.
    Portfolio_id vem do URL, não do body.
    """

    class Meta:
        model = Asset
        fields = ['id', 'ticker', 'quantity', 'purchase_price']
        read_only_fields = ['id']

    def validate(self, attrs):
        portfolio_id = self.context.get('portfolio_id')
        user = self.context['request'].user
        
        if not portfolio_id:
            raise serializers.ValidationError(
                {"portfolio_id": "Portfolio ID não fornecido."}
            )
        
        try:
            portfolio = Portfolio.objects.get(id=portfolio_id, user=user)
        except Portfolio.DoesNotExist:
            raise serializers.ValidationError(
                {"portfolio_id": "Portfólio não encontrado ou não pertence a você."}
            )
        
        attrs['portfolio'] = portfolio
        return attrs

    def create(self, validated_data):
        ticker = validated_data.pop('ticker').upper().strip()
        portfolio = validated_data.pop('portfolio')
        
        # Verificar duplicata
        if Asset.objects.filter(portfolio=portfolio, ticker=ticker).exists():
            raise serializers.ValidationError(
                {"ticker": f"Asset '{ticker}' já existe neste portfólio."}
            )
        # Puxar dados da BRAPI
        try:
            brapi_data = fetch_brapi_data(ticker)
        except Exception as e:
            raise serializers.ValidationError(
                {"ticker": f"Erro ao buscar dados da BRAPI: {str(e)}"}
            )
        
        asset = Asset.objects.create(
            portfolio=portfolio,
            ticker=ticker,
            **validated_data
        )
        return asset