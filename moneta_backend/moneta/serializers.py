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
        # Portfolio será associado ao usuário logado - JWT
        if not self.context:
            raise serializers.ValidationError(
                {"error": "Contexto não fornecido. Usuário não autenticado."}
            )
        
        request = self.context.get('request')
        if not request:
            raise serializers.ValidationError(
                {"error": "Request não encontrado no contexto."}
            )
        
        user = request.user
        if not user or not user.is_authenticated:
            raise serializers.ValidationError(
                {"error": "Usuário não autenticado."}
            )
        
        return Portfolio.objects.create(user=user, **validated_data)

    def update(self, instance, validated_data):
        # Atualizar nome do portfólio
        instance.name = validated_data.get('name', instance.name)
        instance.save()
        return instance


class AssetSerializer(serializers.ModelSerializer):
    """
    Serializer para criar assets em um portfólio.
    Portfolio_id vem do URL, não do body.
    Sincroniza dados da BRAPI automaticamente no cadastro.
    Preço de compra é preenchido automaticamente com o preço atual da BRAPI.
    """
    purchase_price = serializers.DecimalField(max_digits=12, decimal_places=2, required=False, allow_null=True)

    class Meta:
        model = Asset
        fields = ['id', 'ticker', 'quantity', 'purchase_price', 'company_name', 'sector', 
                  'current_price', 'price_change_percent', 'market_cap', 'dividend_yield']
        read_only_fields = ['id', 'company_name', 'sector', 'current_price', 'price_change_percent', 
                           'market_cap', 'dividend_yield']

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
        brapi_data = {}
        try:
            brapi_data = fetch_brapi_data(ticker)
        except Exception as e:
            raise serializers.ValidationError(
                {"ticker": f"Erro ao buscar dados da BRAPI: {str(e)}"}
            )
        
        # Extrair dados relevantes da BRAPI
        # Tenta múltiplos nomes de campo pois BRAPI pode retornar de formas diferentes
        current_price = (
            brapi_data.get('regularMarketPrice') or 
            brapi_data.get('price') or 
            None
        )
        
        if not current_price:
            raise serializers.ValidationError(
                {"ticker": f"Não foi possível obter preço para '{ticker}'. Tente novamente."}
            )
        
        asset_data = {
            'portfolio': portfolio,
            'ticker': ticker,
            **validated_data,
            'company_name': brapi_data.get('longName') or brapi_data.get('shortName'),
            'sector': brapi_data.get('sector'),
            'current_price': current_price,
            'price_change_percent': brapi_data.get('change') or brapi_data.get('changePercent'),
            'market_cap': brapi_data.get('marketCap'),
            'dividend_yield': brapi_data.get('dividendYield'),
        }
        
        # Se purchase_price não foi fornecido, usa o preço atual da BRAPI
        if 'purchase_price' not in validated_data or validated_data.get('purchase_price') is None:
            asset_data['purchase_price'] = current_price
        
        asset = Asset.objects.create(**asset_data)
        return asset

    def update(self, instance, validated_data):
        # Atualizar apenas quantidade e preço de compra
        # Dados da BRAPI permanecem imutáveis
        instance.quantity = validated_data.get('quantity', instance.quantity)
        instance.purchase_price = validated_data.get('purchase_price', instance.purchase_price)
        instance.save()
        return instance