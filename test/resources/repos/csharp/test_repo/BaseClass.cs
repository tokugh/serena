using System;

namespace TestRepo
{
    public abstract class BaseClass
    {
        protected string name;

        public BaseClass(string name)
        {
            this.name = name;
        }

        public abstract void Execute();

        public string GetName()
        {
            return name;
        }
    }

    public interface IProcessable
    {
        void Process();
        string GetType();
    }

    public interface IReadable
    {
        string Read();
    }

    public interface IWritable
    {
        void Write(string data);
    }
}